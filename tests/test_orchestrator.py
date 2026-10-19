"""End-to-end orchestrator runs with a scripted LLM and a toy calculator."""

import json

from interphaise.context import InterfaceContext
from interphaise.llm import ScriptedLLM
from interphaise.orchestrator import Orchestrator, OrchestratorSettings
from interphaise.tools.matcher import MatchSettings
from interphaise.tools.mlip import load_mlip

INTERPHASE = {"chain_of_thought": "...", "interface_type": "interphase", "stack": ["Li", "Li2S", "LiS2"],
              "character": "passivating", "kinetic_argument": "insulating product", "rationale": "toy", "confidence": 0.8}
BAD_STACK = {"interface_type": "interphase", "stack": ["Li", "LiS2", "Li2S", "LiS2"], "character": "passivating",
             "rationale": "wrong"}


def facets(system, user):
    if "Substrate (electrode side): Li," in user:
        return {"pairs": [{"substrate_miller": [1, 1, 0], "film_miller": [1, 1, 1], "rationale": "toy"}]}
    return {"pairs": [{"substrate_miller": [1, 0, 0], "film_miller": [1, 0, 0], "rationale": "toy"}]}


def settings(**kw):
    m = MatchSettings(max_area=120, film_thickness=2, substrate_thickness=2, max_length_tol=0.05)
    return OrchestratorSettings(n_runs=2, max_retries=1, top_k_candidates=1, registry_n_xy=2,
                                registry_gaps=(2.0,), steps=10, match=m, **kw)


def ctx():
    return InterfaceContext(electrode="Li", electrolyte="LiS2", role="anode", voltage=0.0, max_strain=0.05)


def test_dry_run_interphase_branch(tmp_path, toy_bulk, toy_entries):
    llm = ScriptedLLM({"interphase_reasoner": INTERPHASE, "facet_reasoner": facets})
    out = Orchestrator(ctx(), llm, calc=None, settings=settings(), bulk_fn=toy_bulk, entries_fn=toy_entries,
                       run_root=tmp_path).run()
    assert out["reactivity"]["reactive"]
    assert out["decision"].stack == ["Li", "Li2S", "LiS2"]
    assert [p["status"] for p in out["pairs"]] == ["dry_run", "dry_run"]
    log = json.loads((tmp_path.glob("*/decision_log.json").__next__()).read_text())
    assert any(e["stage"] == "stack_check" for e in log["events"])


def test_stack_check_feedback_loop(tmp_path, toy_bulk, toy_entries):
    answers = iter([BAD_STACK, BAD_STACK, INTERPHASE, INTERPHASE])
    llm = ScriptedLLM({"interphase_reasoner": lambda s, u: next(answers), "facet_reasoner": facets})
    orch = Orchestrator(ctx(), llm, calc=None, settings=settings(), bulk_fn=toy_bulk, entries_fn=toy_entries,
                        run_root=tmp_path)
    out = orch.run()
    assert out["decision"].stack == ["Li", "Li2S", "LiS2"]
    second_prompt = [u for s, u in llm.calls if "interphase_reasoner" in s][2]
    assert "not mutually stable" in second_prompt          # feedback reached the LLM


def test_full_run_with_judge(tmp_path, toy_bulk, toy_entries):
    verdicts = iter([{"verdict": "reject", "action": "next_termination", "rationale": "toy reject"}] * 2)

    def judge(system, user):
        return next(verdicts, {"verdict": "accept", "action": "none", "rationale": "ok"})

    llm = ScriptedLLM({"interphase_reasoner": INTERPHASE, "facet_reasoner": facets, "physicality_judge": judge})
    out = Orchestrator(ctx(), llm, calc=load_mlip("lj"), settings=settings(), bulk_fn=toy_bulk,
                       entries_fn=toy_entries, run_root=tmp_path).run()
    statuses = [p["status"] for p in out["pairs"]]
    assert statuses[0] == "ok"                                 # reject → next_termination → accept
    assert out["pairs"][0]["best"].n_relaxations == 3
    log = json.loads((tmp_path.glob("*/decision_log.json").__next__()).read_text())
    assert any(e["kind"] == "transition" and e["output"]["to"] == "next_termination" for e in log["events"])
