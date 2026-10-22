"""LLM-guided PET-MAD pilot: LiNbF6 reference plus two prospective choices (LLM_PETMAD_PILOT_PLAN.md).

The LLM owns the next-material choice and a testable prediction; deterministic code owns menu eligibility,
evidence validation, information boundaries and accounting. Field contract:
data/experiments/llm_petmad_pilot_v1/CONTRACT.md plus Claude's CONTRACT_RESPONSE.md.

Evidence (shared with scripts/analyse_mlip_comparison.py): every `valid` run is re-checked against its
source files before any value can reach a prompt. A failed check makes the run `invalid_evidence`, which
blocks consumption (integrity problem, never a chemistry outcome). A genuine `failed` calculation is
reported as feedback and consumes the slot. Planned primary run IDs are frozen at start, so a missing run
is pending, never silently dropped. Registries of one contact must share build, cell and fixed-mask
identity before the lowest joined energy selects one. Sensitivity values never enter decision prompts.

Accounting: worst-case HTTP attempts are reserved on disk before each call and settled afterwards; an
unknown outcome keeps its reservation, so crashes, decoding errors and resumes cannot exceed the cap.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path

PILOT_VERSION = "llm_petmad_pilot_v2"
STAGES = ("prior", "choose_2", "choose_3", "summary")
CONTACTS = ("cathode", "electrolyte")
ROLES = {"primary", "sensitivity", "consistency"}
NOT_RUN = {"not_run_resource_limit", "not_run_no_admissible_construction"}
STATUSES = {"pending", "valid", "failed", "invalid_evidence"} | NOT_RUN
THERMO_FIELDS = ("penalty", "penalty_bin", "acceptable", "insulating", "band_gap_eV")
IDENTITY_FIELDS = ("candidate_id", "contact", "contact_build_id", "build_sha256", "n_atoms", "fixed_rule",
                   "n_fixed", "fixed_species", "checkpoint_sha256")
WEAK_TOLERANCE_J_M2 = 0.1     # reporting convention for "unresolved" weak contact, not an uncertainty
HTTP_ATTEMPT_CAP = 10
MAX_HTTP_PER_CALL = 3         # make_llm default retries: worst-case HTTP attempts inside one call
MAX_FORMAT_ATTEMPTS = 2       # per stage; every attempt is charged against the HTTP cap
MAX_PROMPT_CHARS = 16000      # ~8.6k input tokens at 1.86 chars/token: makes the cost ceiling enforceable
EV_A2_TO_J_M2 = 16.021766208
TOL_J_M2 = 1e-6

SYSTEM_PROMPT = """You are a battery materials scientist choosing which coating to evaluate next with an
interatomic-potential (PET-MAD) interface calculation. Coatings sit between a LiCoO2 cathode and a Li6PS5Cl
electrolyte at 4 V. The fixed brief: favourable trade-offs between the frozen thermodynamic penalty (lower is
better) and the weaker of the two validated contact adhesion works W_adh (higher is better). Strong adhesion
cannot make a thermodynamically rejected coating acceptable. Use only the candidate cards, your earlier
decisions and the feedback you are shown; do not invent computed values. Answer with one JSON object in the
requested schema."""


class Pending(Exception):
    """Required feedback is not yet terminal (or a planned run is missing); save state and resume later."""


class Blocked(Exception):
    """Evidence integrity problem: feedback must not be consumed until it is resolved."""


def digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def _resolve(path, root):
    p = Path(path)
    return p if p.is_absolute() else Path(root) / p


def load_index(path):
    """Structural validation of the campaign index written by the PET-MAD side."""
    index = json.loads(Path(path).read_text())
    problems, seen = [], set()
    for key in ("schema_version", "checkpoint_sha256", "menu", "runs"):
        if key not in index:
            problems.append(f"index missing {key}")
    menu_ids = {c["candidate_id"] for c in index.get("menu", [])}
    for r in index.get("runs", []):
        rid = r.get("run_id")
        if rid in seen:
            problems.append(f"duplicate run_id {rid}")
        seen.add(rid)
        if r.get("candidate_id") not in menu_ids:
            problems.append(f"{rid}: candidate not in menu")
        if r.get("contact") not in CONTACTS or r.get("role") not in ROLES:
            problems.append(f"{rid}: bad contact/role")
        if r.get("status") not in STATUSES:
            problems.append(f"{rid}: bad status {r.get('status')!r}")
        if r.get("status") in NOT_RUN and (r.get("role") != "sensitivity" or not r.get("failure_reason")):
            problems.append(f"{rid}: {r.get('status')} is only for sensitivity rows and needs a reason")
        if r.get("checkpoint_sha256") != index.get("checkpoint_sha256"):
            problems.append(f"{rid}: checkpoint differs from the campaign checkpoint")
        if r.get("status") == "failed" and not r.get("failure_reason"):
            problems.append(f"{rid}: failed run without failure_reason")
        if r.get("status") != "valid" and r.get("W_adh_J_m2") is not None:
            problems.append(f"{rid}: non-valid run carries a W_adh")
    if problems:
        raise ValueError("Invalid campaign index:\n  " + "\n  ".join(problems))
    return index


def source_problems(run, checkpoint, root):
    """Re-check one `valid` run against its result and separation files; [] means the work is validated."""
    problems = []
    for key in ("W_adh_J_m2", "joined_energy_eV", "area_A2"):
        if not _finite(run.get(key)):
            problems.append(f"index {key} not finite")
    if run.get("W_sep_J_m2") is not None and not _finite(run["W_sep_J_m2"]):
        problems.append("index W_sep_J_m2 not finite")
    if not run.get("result_path") or not _resolve(run["result_path"], root).exists():
        return problems + ["result file missing"]
    raw = _resolve(run["result_path"], root).read_bytes()
    if run.get("result_sha256") and hashlib.sha256(raw).hexdigest() != run["result_sha256"]:
        problems.append("result file hash differs from index")
    res = json.loads(raw)
    if res.get("checkpoint_sha256") != checkpoint:
        problems.append("result checkpoint differs from campaign")
    if res.get("numerically_valid") is not True:
        problems.append("result not numerically_valid")
    rel = res.get("relaxations", {})
    for part in ("interface", "film", "substrate"):
        r = rel.get(part, {})
        if not (r.get("converged") and r.get("finite") and _finite(r.get("final_energy_eV"))):
            problems.append(f"{part} relaxation not converged/finite")
        elif not (_finite(r.get("max_free_force_eV_A")) and r["max_free_force_eV_A"] <= r.get("fmax_target_eV_A", -1)):
            problems.append(f"{part} free force above target")
    area = res.get("area_A2")
    if not (_finite(area) and area > 0):
        return problems + ["invalid area in result"]
    if _finite(run.get("area_A2")) and abs(run["area_A2"] - area) > 1e-6:
        problems.append("area differs from index")
    if run.get("n_atoms") is not None and run["n_atoms"] != res.get("n_atoms"):
        problems.append("atom count differs from index")
    if run.get("n_fixed") is not None and res.get("n_fixed") is not None and run["n_fixed"] != res["n_fixed"]:
        problems.append("fixed-atom count differs from index")
    if problems:
        return problems
    e = {p: rel[p]["final_energy_eV"] for p in ("interface", "film", "substrate")}
    w = (e["film"] + e["substrate"] - e["interface"]) / area * EV_A2_TO_J_M2
    if abs(w - run["W_adh_J_m2"]) > TOL_J_M2 or not _finite(res.get("work_of_adhesion_J_m2")) \
            or abs(w - res["work_of_adhesion_J_m2"]) > TOL_J_M2:
        problems.append(f"W_adh arithmetic mismatch (recomputed {w:.6f})")
    if abs(e["interface"] - run["joined_energy_eV"]) > 1e-6:
        problems.append("joined energy differs from interface final energy")
    if run.get("W_sep_J_m2") is not None:
        sep_path = run.get("separation_path")
        if not sep_path or not _resolve(sep_path, root).exists():
            problems.append("W_sep given without separation file")
        else:
            s = json.loads(_resolve(sep_path, root).read_text())
            keys = ("E_film_rigid_eV", "E_substrate_rigid_eV", "E_interface_eV", "area_A2")
            if not all(_finite(s.get(k)) for k in keys) or s["area_A2"] <= 0:
                problems.append("separation values not finite")
            else:
                ws = (s["E_film_rigid_eV"] + s["E_substrate_rigid_eV"] - s["E_interface_eV"]) / s["area_A2"] * EV_A2_TO_J_M2
                if s.get("checkpoint_sha256") != checkpoint:
                    problems.append("separation checkpoint differs")
                if abs(s["area_A2"] - area) > 1e-6 or abs(s["E_interface_eV"] - e["interface"]) > 1e-6:
                    problems.append("separation cell/energy does not match the joined run")
                if abs(ws - run["W_sep_J_m2"]) > TOL_J_M2:
                    problems.append(f"W_sep arithmetic mismatch (recomputed {ws:.6f})")
    return problems


def evaluate_runs(index, root):
    """Run copies with `evidence` (valid/failed/pending/invalid_evidence/unavailable) and `problems`."""
    out = {}
    for r in index["runs"]:
        r = dict(r)
        r["problems"] = source_problems(r, index["checkpoint_sha256"], root) if r["status"] == "valid" else []
        r["evidence"] = ("invalid_evidence" if r["problems"] else
                         "unavailable" if r["status"] in NOT_RUN else r["status"])
        out[r["run_id"]] = r
    return out


def comparable_problems(primary):
    """Registries of one contact must share build, cell and fixed-mask identity (lateral shifts allowed)."""
    problems = []
    ids = [r.get("registry_id") for r in primary]
    if len(ids) != len(set(ids)):
        problems.append("duplicate registry_id")
    for field in IDENTITY_FIELDS:
        if len({json.dumps(r.get(field), sort_keys=True) for r in primary}) > 1:
            problems.append(f"registries differ in {field}")
    areas = [r.get("area_A2") for r in primary if _finite(r.get("area_A2"))]
    if areas and max(areas) - min(areas) > 1e-6:
        problems.append("registries differ in area")
    return problems


def thermo_card(table, candidate_id):
    row = next((r for r in table["results"] if r["candidate_id"] == candidate_id), None)
    if row is None:
        raise ValueError(f"{candidate_id} not in the frozen thermodynamic table")
    return {k: row.get(k) for k in THERMO_FIELDS}


def contact_summary(runs, contact):
    """Validated selection for one contact from evaluated primary runs (no consumption checks here)."""
    primary = [r for r in runs if r["contact"] == contact and r["role"] == "primary"]
    valid = [r for r in primary if r["evidence"] == "valid"]
    chosen = min(valid, key=lambda r: r["joined_energy_eV"]) if valid else None
    return dict(status="valid" if chosen else "failed", selected_run_id=chosen and chosen["run_id"],
                W_adh_J_m2=chosen and chosen["W_adh_J_m2"], W_sep_J_m2=chosen and chosen.get("W_sep_J_m2"),
                registry_range_J_m2=[min(r["W_adh_J_m2"] for r in valid), max(r["W_adh_J_m2"] for r in valid)] if valid else None,
                registries=[dict(run_id=r["run_id"], registry_id=r.get("registry_id"), registry=r.get("registry"),
                                 status=r["evidence"], W_adh_J_m2=r["W_adh_J_m2"] if r["evidence"] == "valid" else None,
                                 failure_reason=r.get("failure_reason"), warnings=r.get("warnings", []))
                            for r in sorted(primary, key=lambda r: r["run_id"])])


def feedback_bundle(index, table, candidate_id, root, planned=None):
    """Consumable primary feedback for one coating, or raise Pending/Blocked. Sensitivity values withheld."""
    card = next(c for c in index["menu"] if c["candidate_id"] == candidate_id)
    evaluated = evaluate_runs(index, root)
    runs = [r for r in evaluated.values() if r["candidate_id"] == candidate_id and r["role"] != "consistency"]
    primary_ids = sorted(r["run_id"] for r in runs if r["role"] == "primary")
    if planned is not None and primary_ids != sorted(planned):
        missing = sorted(set(planned) - set(primary_ids))
        if missing:
            raise Pending(f"{candidate_id}: planned primary runs missing from index: {missing}")
        raise Blocked(f"{candidate_id}: unplanned primary runs in index: {sorted(set(primary_ids) - set(planned))}")
    integrity = [f"{r['run_id']}: {'; '.join(r['problems']) or r['status']}" for r in runs if r["evidence"] == "invalid_evidence"]
    if integrity:
        raise Blocked(f"{candidate_id}: invalid evidence: {integrity}")
    contacts = {}
    for contact in CONTACTS:
        primary = [r for r in runs if r["contact"] == contact and r["role"] == "primary"]
        if not primary or any(r["evidence"] == "pending" for r in primary):
            raise Pending(f"{candidate_id} {contact}: primary runs not terminal")
        problems = comparable_problems(primary)
        if problems:
            raise Blocked(f"{candidate_id} {contact}: registries not comparable: {problems}")
        contacts[contact] = contact_summary(runs, contact)
    w = {c: contacts[c]["W_adh_J_m2"] for c in CONTACTS}
    both = all(v is not None for v in w.values())
    weaker = ("unresolved" if not both or abs(w["cathode"] - w["electrolyte"]) < WEAK_TOLERANCE_J_M2
              else min(CONTACTS, key=lambda c: w[c]))
    primary = [r for r in runs if r["role"] == "primary"]
    known = [r for r in primary if r.get("calculator_calls") is not None]
    return dict(candidate_id=candidate_id, formula=card["formula"], thermo=thermo_card(table, candidate_id),
                contacts=contacts, weaker_contact=weaker, min_W_adh_J_m2=min(w.values()) if both else None,
                sensitivity=[dict(run_id=r["run_id"], contact=r["contact"], kind=r.get("sensitivity_kind"),
                                  availability="unavailable: " + r["failure_reason"] if r["evidence"] == "unavailable"
                                  else "planned; not part of this decision")
                             for r in sorted(runs, key=lambda r: r["run_id"]) if r["role"] == "sensitivity"],
                primary_cost=dict(calculator_calls=sum(r["calculator_calls"] for r in known),
                                  runs_with_unknown_cost=len(primary) - len(known)),
                limitations=card.get("limitations", []))


def validate_decision(stage, response, remaining):
    """Check one parsed LLM response; raise ValueError with a reason the model can act on."""
    if not isinstance(response, dict):
        raise ValueError("Return one JSON object")
    if stage == "summary":
        if not isinstance(response.get("summary"), str) or not response["summary"].strip():
            raise ValueError("Return {'summary': str, 'prior_prediction_assessment': str}")
        if not isinstance(response.get("prior_prediction_assessment"), str) or not response["prior_prediction_assessment"].strip():
            raise ValueError("prior_prediction_assessment must state which earlier predictions held or failed")
        return response
    shortlist = response.get("ordered_shortlist")
    if (not isinstance(shortlist, list) or len(shortlist) != len(set(shortlist))
            or set(shortlist) != set(remaining)):
        raise ValueError(f"ordered_shortlist must rank exactly these unevaluated IDs once: {sorted(remaining)}")
    if not isinstance(response.get("hypothesis"), str) or not response["hypothesis"].strip():
        raise ValueError("Each decision needs a nonempty hypothesis")
    if stage == "prior":
        return response
    if response.get("selected_id") != shortlist[0]:
        raise ValueError("selected_id must be the first ID of ordered_shortlist")
    if response.get("predicted_weaker_contact") not in (*CONTACTS, "unresolved"):
        raise ValueError("predicted_weaker_contact must be cathode, electrolyte or unresolved")
    ranges = response.get("predicted_W_adh_J_m2")
    for c in CONTACTS:
        r = (ranges or {}).get(c)
        if not (isinstance(r, list) and len(r) == 2 and all(_finite(x) for x in r) and r[0] <= r[1]):
            raise ValueError(f"predicted_W_adh_J_m2.{c} must be a finite ordered interval [low, high] in J/m2")
    if not isinstance(response.get("change_trigger"), str) or not response["change_trigger"].strip():
        raise ValueError("change_trigger must name an observation that would change the next choice")
    if stage == "choose_3":
        if not (isinstance(response.get("supporting_observations"), list) and response["supporting_observations"]):
            raise ValueError("supporting_observations must cite the specific feedback behind this choice")
        if not isinstance(response.get("prior_prediction_assessment"), str) or not response["prior_prediction_assessment"].strip():
            raise ValueError("prior_prediction_assessment must say whether the feedback supports or contradicts "
                             "your earlier prediction and whether your choice changes")
    return response


DECISION = ('"ordered_shortlist": [ids], "selected_id": first id, "hypothesis": str, '
            '"predicted_weaker_contact": "cathode"|"electrolyte"|"unresolved", '
            '"predicted_W_adh_J_m2": {"cathode": [low, high], "electrolyte": [low, high]}, "change_trigger": str')
OUTPUT_SCHEMA = {
    "prior": '{"ordered_shortlist": [ids], "hypothesis": str}',
    "choose_2": "{" + DECISION + "}",
    "choose_3": "{" + DECISION + ', "supporting_observations": [str], "prior_prediction_assessment": str}',
    "summary": '{"summary": str, "prior_prediction_assessment": str}',
}
QUESTION = {
    "prior": "Rank the unevaluated coatings from chemistry alone.",
    "choose_2": "Using the reference feedback, choose the next coating and predict its W_adh at both contacts.",
    "choose_3": ("Compare the new feedback with your previous decision and prediction (previous_decisions). Say "
                 "whether it supports or contradicts that prediction and whether your choice changes; then choose."),
    "summary": "Assess which of your earlier predictions held, failed or remain unresolved, and summarise.",
}


class Pilot:
    """Resumable state machine. One process owns the state file (lock); every record is hashed and kept."""

    def __init__(self, state_path, index_path, table_path, *, reference_id, mode, settings, root=".",
                 http_cap=HTTP_ATTEMPT_CAP, max_http_per_call=MAX_HTTP_PER_CALL, allow_small_menu=False,
                 include_prior=True):
        from interphaise.tools.thermo_dataset import verify_hash
        self.path, self.index_path, self.root = Path(state_path), Path(index_path), Path(root)
        self.table = json.loads(Path(table_path).read_text())
        verify_hash(self.table)  # actual contents, not just the declared field
        self.lock = self.path.with_suffix(".lock")
        try:
            fd = os.open(self.lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise RuntimeError(f"{self.lock} exists: another process owns this pilot state (remove only if it is stale)") from None
        os.write(fd, str(os.getpid()).encode())
        os.close(fd)
        try:
            self._open(reference_id, mode, settings, http_cap, max_http_per_call, allow_small_menu, include_prior)
        except BaseException:
            self.close()
            raise

    def _open(self, reference_id, mode, settings, http_cap, max_http_per_call, allow_small_menu, include_prior):
        if self.path.exists():
            self.state = json.loads(self.path.read_text())
            if (self.state["mode"], self.state["settings"]) != (mode, settings):
                raise ValueError("Execution mode/settings differ from the saved pilot state")
            if self.state["table_sha256"] != self.table["sha256"]:
                raise ValueError("Thermodynamic table differs from the saved pilot state")
            for r in self.state["stages"]:
                if r.get("record_sha256") and digest({k: v for k, v in r.items() if k != "record_sha256"}) != r["record_sha256"]:
                    raise ValueError(f"Stage record hash mismatch ({r['stage']})")
            for cid, snap in self.state["snapshots"].items():
                if digest(snap["bundle"]) != snap["sha256"]:
                    raise ValueError(f"Feedback snapshot hash mismatch ({cid})")
            return
        index = load_index(self.index_path)
        feasible = [c["candidate_id"] for c in index["menu"] if c.get("feasible")]
        if reference_id not in feasible:
            raise ValueError("Reference must be a feasible menu item")
        if len(feasible) - 1 < 3 and not allow_small_menu:
            raise ValueError(f"Only {len(feasible) - 1} unevaluated alternatives; report before live calls")
        planned = {cid: sorted(r["run_id"] for r in index["runs"] if r["candidate_id"] == cid and r["role"] == "primary")
                   for cid in feasible}
        if any(not ids for ids in planned.values()):
            raise ValueError("Every feasible candidate needs its planned primary runs listed (pending) in the index")
        self.state = dict(
            pilot_version=PILOT_VERSION, created_at=_now(), mode=mode, settings=settings, reference_id=reference_id,
            feasible=feasible, planned_primary=planned, menu_sha256=digest(index["menu"]),
            manifest_sha256=index.get("manifest_sha256"), table_sha256=self.table["sha256"], http_cap=http_cap,
            max_http_per_call=max_http_per_call, http_attempts_used=0, http_reserved_unsettled=0, stages=[],
            snapshots={}, evaluated=[reference_id], selected=[],
            plan=[s for s in STAGES if include_prior or s != "prior"], status="running")
        self._save()

    def close(self):
        if self.lock.exists():
            self.lock.unlink()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _save(self):
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=2, allow_nan=False))
        tmp.replace(self.path)

    def next_stage(self):
        if self.state["status"] != "running":
            return None  # a stopped or completed pilot never advances on resume
        done = {s["stage"] for s in self.state["stages"] if s.get("parsed") is not None}
        return next((s for s in self.state["plan"] if s not in done), None)

    def _cards(self, index):
        return [dict(candidate_id=c["candidate_id"], formula=c["formula"], thermo=thermo_card(self.table, c["candidate_id"]),
                     descriptors=c.get("descriptors", {}), limitations=c.get("limitations", []))
                for c in index["menu"] if c["candidate_id"] in self.state["feasible"]]

    def _snapshot(self, index, cid):
        """Frozen primary feedback: built once when first revealed, then reused verbatim."""
        if cid not in self.state["snapshots"]:
            bundle = feedback_bundle(index, self.table, cid, self.root, self.state["planned_primary"][cid])
            self.state["snapshots"][cid] = dict(bundle=bundle, sha256=digest(bundle), frozen_at=_now())
            self._save()
        return self.state["snapshots"][cid]["bundle"]

    def _previous_decisions(self):
        keep = ("ordered_shortlist", "selected_id", "hypothesis", "predicted_weaker_contact", "predicted_W_adh_J_m2",
                "change_trigger", "supporting_observations", "prior_prediction_assessment")
        return [dict(stage=s["stage"], **{k: s["parsed"][k] for k in keep if k in s["parsed"]})
                for s in self.state["stages"] if s.get("parsed") is not None]

    def run_stage(self, llm):
        stage = self.next_stage()
        if stage is None:
            return None
        index = load_index(self.index_path)
        if digest(index["menu"]) != self.state["menu_sha256"]:
            raise ValueError("Menu changed after the pilot started")
        reveal = {"prior": [], "choose_2": [self.state["reference_id"]],
                  "choose_3": [self.state["reference_id"], *self.state["selected"][:1]],
                  "summary": [self.state["reference_id"], *self.state["selected"][:2]]}[stage]
        bundles = [self._snapshot(index, cid) for cid in reveal]  # Pending/Blocked raised before any call
        for b in bundles:
            if b["candidate_id"] not in self.state["evaluated"]:
                self.state["evaluated"].append(b["candidate_id"])
        remaining = [c for c in self.state["feasible"] if c not in self.state["evaluated"] and c not in self.state["selected"]]
        user = dict(stage=stage, question=QUESTION[stage], candidates=self._cards(index), evaluated=self.state["evaluated"],
                    unevaluated=remaining, feedback=bundles, previous_decisions=self._previous_decisions(),
                    output_schema=OUTPUT_SCHEMA[stage])
        feedback = ""
        for attempt in range(MAX_FORMAT_ATTEMPTS):
            prompt = json.dumps({**user, "validation_feedback": feedback}, sort_keys=True)
            if len(prompt) > MAX_PROMPT_CHARS:
                return self._stop(f"stopped: {stage} prompt exceeds {MAX_PROMPT_CHARS} characters")
            worst = self.state["max_http_per_call"]
            if self.state["http_attempts_used"] + worst > self.state["http_cap"]:
                return self._stop("stopped: HTTP attempt cap reached")
            self.state["http_attempts_used"] += worst          # durable reservation before transport
            self.state["http_reserved_unsettled"] += worst
            self._save()
            record = dict(stage=stage, attempt=attempt, prompt=prompt, feedback_sha256=[digest(b) for b in bundles],
                          started_at=_now(), parsed=None)
            if hasattr(llm, "last_metadata"):
                llm.last_metadata = None                          # never settle on a stale previous call
            try:
                response = llm(SYSTEM_PROMPT, prompt)
                record["response"] = response
                record["parsed"] = validate_decision(stage, response, remaining)
            except Exception as exc:
                feedback = f"{type(exc).__name__}: {exc}"
                record["error"] = feedback
            meta = getattr(llm, "last_metadata", None)
            record["llm_metadata"] = meta
            used = (meta or {}).get("http_attempts")
            if isinstance(used, int) and 0 <= used <= worst:      # settle; unknown keeps the full reservation
                self.state["http_attempts_used"] -= worst - used
            self.state["http_reserved_unsettled"] -= worst
            record["http_attempts_charged"] = used if isinstance(used, int) and 0 <= used <= worst else worst
            record["frozen_at"] = _now()
            record["record_sha256"] = digest({k: v for k, v in record.items() if k != "record_sha256"})
            self.state["stages"].append(record)
            if record["parsed"] is not None:
                if stage in ("choose_2", "choose_3"):
                    self.state["selected"].append(record["parsed"]["selected_id"])
                if stage == "summary":
                    self.state["status"] = "complete"
                self._save()
                return record
            self._save()
        return self._stop(f"stopped: {stage} failed validation")

    def _stop(self, reason):
        self.state["status"] = reason
        self._save()
        return None

    def assessment(self):
        """Deterministic prediction checks and the decision comparison (descriptive only)."""
        decisions = {s["stage"]: s["parsed"] for s in self.state["stages"] if s.get("parsed")}
        rows = []
        for stage in ("choose_2", "choose_3"):
            if stage not in decisions:
                continue
            d = decisions[stage]
            snap = self.state["snapshots"].get(d["selected_id"])
            if snap is None:
                rows.append(dict(stage=stage, candidate_id=d["selected_id"], status="not yet revealed"))
                continue
            b, checks = snap["bundle"], {}
            for c in CONTACTS:
                lo, hi = d["predicted_W_adh_J_m2"][c]
                obs = b["contacts"][c]["W_adh_J_m2"]
                checks[c] = dict(predicted=[lo, hi], width=hi - lo, observed=obs,
                                 in_range=None if obs is None else lo <= obs <= hi,
                                 miss=None if obs is None else max(lo - obs, obs - hi, 0.0))
            rows.append(dict(stage=stage, candidate_id=d["selected_id"], contacts=checks,
                             weaker_predicted=d["predicted_weaker_contact"], weaker_observed=b["weaker_contact"],
                             weaker_agrees=None if b["weaker_contact"] == "unresolved"
                             else d["predicted_weaker_contact"] == b["weaker_contact"]))
        comparison = None
        if "choose_2" in decisions and "choose_3" in decisions:
            initial = [c for c in decisions["choose_2"]["ordered_shortlist"] if c != decisions["choose_2"]["selected_id"]]
            comparison = dict(initial_next=initial[0] if initial else None, chosen=decisions["choose_3"]["selected_id"],
                              changed=bool(initial) and initial[0] != decisions["choose_3"]["selected_id"],
                              note="Decision comparison at a common information state; the unchosen coating has no measured outcome.")
        return dict(predictions=rows, decision_comparison=comparison, http_attempts_used=self.state["http_attempts_used"])


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
