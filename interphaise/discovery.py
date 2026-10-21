"""Budgeted candidate search against the frozen query boundary (``BenchmarkQueries``).

Arms: random; upfront (one shortlist, no feedback); sequential (one choice per turn,
sees its own earlier choices, no outcomes); sequential_ids (as sequential, but sees only
earlier candidate IDs, no rationales); iterative (sees queried outcomes); shuffled (as
iterative, but outcomes are permuted among already-queried candidates).
The proposer never sees unqueried outcomes, the answer table, provenance or timing.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from .discovery_evaluator import ranking_key
from .tools.thermo_dataset import digest

PROMPT_VERSION = "v3-2026-10-21c-charged-ids"
LLM_STRATEGIES = {"iterative", "sequential", "sequential_ids", "shuffled", "upfront"}
STRATEGIES = LLM_STRATEGIES | {"random"}
PROMPT = """You are a battery coating discovery scientist choosing which candidate coatings to evaluate.
Select only from the available candidates, by candidate_id. Formulas are not unique: polymorphs are separate candidates.
Use chemical hypotheses and any calculation results you are shown. Do not invent computed outcomes.
The task, operating conditions and fixed objective are supplied; you cannot change them.
Return {"proposals": [{"candidate_id": "exact available candidate_id", "hypothesis": "concise chemical rationale",
"motivation": "the earlier observation that motivated this choice, or \\"none\\"", "mode": "explore" or "refine"}]}.
"explore" means a chemically different family from earlier choices; "refine" means close to an earlier choice.
Return exactly as many proposals as the "count" field of the request, no more and no fewer.
Copy each candidate_id character for character from the available list. Select distinct IDs.
Each submitted candidate_id costs one evaluation, including invalid or repeated IDs.
Another polymorph of the same formula is a separate candidate and costs another evaluation."""

# Outcome fields the iterative arm may see; provenance, timing and diagnostics stay out of prompts.
FEEDBACK_FIELDS = ("candidate_id", "formula", "status", "error", "insulating", "band_gap_eV",
                   "self_decomposition_penalty", "contact_reaction_energies", "contacts",
                   "penalty", "penalty_bin", "acceptable", "warnings", "energy_units")
PUBLIC_TASK_FIELDS = ("endpoints", "voltage_V", "objective", "instructions")
HASH_FIELDS = ("objective_sha256", "pool_sha256", "benchmark_sha256")


def run_discovery(queries, *, strategy="iterative", llm=None, seed=0, output: Path | None = None,
                  max_proposal_attempts=3, metadata=None):
    """One independent run; ``queries`` is a fresh BenchmarkQueries whose budget is the run budget."""
    if strategy not in STRATEGIES:
        raise ValueError("Unknown strategy")
    if strategy in LLM_STRATEGIES and llm is None:
        raise ValueError("This strategy requires an LLM")
    if max_proposal_attempts < 1:
        raise ValueError("Proposal attempts must be positive")
    task, budget = queries.task(), queries.remaining
    public_task = {k: task[k] for k in PUBLIC_TASK_FIELDS}
    pool = queries.available()
    random.Random(seed).shuffle(pool)  # displayed order; same seed => same order across arms
    formula = {c["candidate_id"]: c["formula"] for c in pool}
    shuffle_rng = random.Random(f"shuffle-{seed}")
    shown_bundles = []  # shuffled arm: displayed outcome per history slot
    real_slots = []     # shuffled arm: slots holding a first query of a pool candidate
    state = dict(strategy=strategy, seed=seed, budget=budget, prompt_version=PROMPT_VERSION,
                 hashes={k: task[k] for k in HASH_FIELDS}, objective=task["objective"],
                 metadata=metadata or {}, proposal_attempts=[], history=[], trace=[],
                 displayed_sources=[], status="running")

    def save():
        if output is not None:
            output.parent.mkdir(parents=True, exist_ok=True)
            temp = output.with_suffix(".tmp")
            temp.write_text(json.dumps(state, indent=2, allow_nan=False))
            temp.replace(output)

    def visible(result):
        return {k: result[k] for k in FEEDBACK_FIELDS if k in result}

    def shown_history():
        if strategy == "iterative":
            return [dict(proposal=h["proposal"], result=visible(h["result"])) for h in state["history"]]
        if strategy == "shuffled":
            # Relabel each displayed bundle with the candidate it is shown next to.
            # Charged invalid/repeated IDs are never permuted, so their own error stays in place.
            return [dict(proposal=h["proposal"],
                         result=dict(b, candidate_id=h["result"].get("candidate_id"),
                                     formula=h["result"].get("formula")) if i in real_slots else b)
                    for i, (h, b) in enumerate(zip(state["history"], shown_bundles))]
        if strategy == "sequential_ids":
            return [dict(proposal={"candidate_id": h["proposal"]["candidate_id"]}) for h in state["history"]]
        return [dict(proposal=h["proposal"]) for h in state["history"]]

    def propose(count):
        queried = {h["result"]["candidate_id"] for h in state["history"]
                   if isinstance(h["result"].get("candidate_id"), str)}
        available = [c for c in pool if c["candidate_id"] not in queried]
        feedback = ""
        for _ in range(max_proposal_attempts):
            user = json.dumps(dict(task=public_task, available=available, count=count,
                                   evaluated=shown_history(), validation_feedback=feedback))
            attempt = {"prompt": user}
            try:
                response = llm(PROMPT, user)
                attempt["response"] = response
                attempt["llm_metadata"] = getattr(llm, "last_metadata", None)
                proposals = response["proposals"]
                if not isinstance(proposals, list) or len(proposals) != count:
                    raise ValueError(f"Return exactly {count} proposal(s); got "
                                     f"{len(proposals) if isinstance(proposals, list) else 'none'}")
                # Missing proposal fields are a message-format failure. Once a
                # candidate_id is supplied, query() owns validation and charges it.
                if any(not isinstance(p, dict) or "candidate_id" not in p for p in proposals):
                    raise ValueError("Each proposal needs a candidate_id field")
                if any(not isinstance(p.get("hypothesis"), str) or not p["hypothesis"].strip() for p in proposals):
                    raise ValueError("Each proposal needs a nonempty hypothesis")
                if any(not isinstance(p.get("motivation"), str) or p.get("mode") not in {"explore", "refine"}
                       for p in proposals):
                    raise ValueError('Each proposal needs a motivation string and mode "explore" or "refine"')
            except Exception as exc:
                attempt["llm_metadata"] = getattr(llm, "last_metadata", None)
                feedback = f"{type(exc).__name__}: {exc}"
                attempt["error"] = feedback
                state["proposal_attempts"].append(attempt)
                save()
                continue
            state["proposal_attempts"].append(attempt)
            save()
            return proposals
        raise ValueError("Proposal attempts exhausted: " + feedback)

    save()
    try:
        planned = []
        if strategy == "upfront":
            planned = propose(budget)
        elif strategy == "random":
            planned = [{"candidate_id": c["candidate_id"], "hypothesis": "random baseline"} for c in pool[:budget]]
        best = None
        for step in range(budget):
            proposal = propose(1)[0] if strategy not in {"upfront", "random"} else planned[step]
            cid = proposal["candidate_id"]
            first_query = (isinstance(cid, str) and cid in formula
                           and all(h["result"].get("candidate_id") != cid for h in state["history"]))
            result = queries.query(cid)
            state["history"].append(dict(proposal=proposal, result=result))
            if strategy == "shuffled":
                # Inside-out Fisher-Yates over real evaluations only: their displayed outcomes form a
                # uniform permutation of queried outcomes, and at most one earlier display changes per
                # turn. Known limits: a moved outcome can contradict a rationale written when it was
                # shown elsewhere, reaction products can hint at the true source, and the first real
                # outcome cannot be shuffled.
                shown_bundles.append(visible(result))
                if first_query:
                    real_slots.append(len(shown_bundles) - 1)
                    j = real_slots[shuffle_rng.randint(0, len(real_slots) - 1)]
                    shown_bundles[-1], shown_bundles[j] = shown_bundles[j], shown_bundles[-1]
                state["displayed_sources"].append([b.get("candidate_id") for b in shown_bundles])
            if ranking_key(result)[0] and (best is None or ranking_key(result) > ranking_key(best)):
                best = result
            state["trace"].append(dict(evaluations=step + 1,
                                       best_candidate_id=best["candidate_id"] if best else None,
                                       best_rank=list(ranking_key(best)) if best else None,
                                       any_acceptable=any(h["result"].get("acceptable") for h in state["history"])))
            save()
        state["status"] = "complete"
    except Exception as exc:
        state["status"] = "failed"
        state["error"] = f"{type(exc).__name__}: {exc}"
        save()
        raise
    save()
    return state


def random_success_curve(n_pool, n_successes, budget):
    """P(at least one success in k uniform draws without replacement), k = 1..budget."""
    return [1 - math.comb(n_pool - n_successes, k) / math.comb(n_pool, k) for k in range(1, budget + 1)]


def write_synthetic_benchmark(directory: Path, seed=0, families=5, per_family=10):
    """Fake pool + benchmark files readable by BenchmarkQueries(..., allow_draft=True); not chemistry.

    Penalties cluster by family so feedback is informative. Returns (pool_path, benchmark_path).
    """
    rng = random.Random(seed)
    objective = {"version": "synthetic", "min_band_gap_eV": 2.0, "bin_width_eV": 0.02, "acceptable_penalty_eV": 0.05}
    candidates, results = [], []
    for f in range(families):
        mean = rng.uniform(0.0, 0.25)
        for i in range(per_family):
            cid, formula = f"syn-{f}-{i:02d}", f"X{f}Y{i}"
            candidates.append(dict(candidate_id=cid, formula=formula, family=f"family-{f}"))
            if rng.random() < 0.05:
                results.append(dict(candidate_id=cid, formula=formula, status="failed", error="synthetic failure"))
                continue
            penalty = max(0.0, mean + rng.gauss(0, 0.04))
            insulating = rng.random() > 0.05
            results.append(dict(candidate_id=cid, formula=formula, status="ok", insulating=insulating,
                                penalty=penalty, penalty_bin=math.floor(penalty / 0.02 + 1e-12),
                                acceptable=insulating and penalty <= 0.05, energy_units="synthetic"))
    pool = dict(candidates=candidates, seed=seed, status="synthetic")
    pool["sha256"] = digest(pool)
    benchmark = dict(status="synthetic", objective=objective, objective_sha256=digest(objective),
                     pool_sha256=pool["sha256"], voltage_V=4.0, results=results,
                     endpoints={"electrode": {"formula": "SYN-CATHODE"}, "electrolyte": {"formula": "SYN-ELECTROLYTE"}})
    benchmark["sha256"] = digest(benchmark)
    directory.mkdir(parents=True, exist_ok=True)
    paths = directory / "synthetic_pool.json", directory / "synthetic_benchmark.json"
    for path, data in zip(paths, (pool, benchmark)):
        path.write_text(json.dumps(data, indent=2))
    return paths
