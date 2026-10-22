"""Coating screen + ranker on the toy Li–S chemistry.

Toy story: Li | LiS2 reacts (Li2S forms); a Li2S "coating" is stable against
both sides, so it must outrank the uncoated baseline.
"""

import json

from interphaise.llm import ScriptedLLM
from interphaise.orchestrator import OrchestratorSettings
from interphaise.ranker import CoatingRow, ContactResult, rank, to_markdown
from interphaise.screen import ScreenConfig, run_screen
from interphaise.tools.matcher import MatchSettings

from tests.test_orchestrator import facets


def interphase_reasoner(system, user):
    if "Electrode side: Li (" in user and "Electrolyte side: LiS2" in user:
        return {"interface_type": "interphase", "stack": ["Li", "Li2S", "LiS2"], "character": "passivating",
                "rationale": "Li2S forms and is insulating", "confidence": 0.8}
    return {"interface_type": "sharp", "stack": [], "character": "none", "rationale": "stable"}


CFG = ScreenConfig(electrode="Li", electrolyte="LiS2", coatings=["Li2S"], voltage=0.0, role="anode",
                   max_strain=0.05)


def test_screen_decision_only(tmp_path, toy_bulk, toy_entries):
    llm = ScriptedLLM({"interphase_reasoner": interphase_reasoner, "facet_reasoner": facets})
    out = run_screen(CFG, llm, settings=OrchestratorSettings(n_runs=2, build_structures=False),
                     bulk_fn=toy_bulk, entries_fn=toy_entries, run_root=tmp_path)
    llm_rank = [(r["coating"], r["tier"]) for r in out["ranking"]]
    assert llm_rank == [("Li2S", 1), ("none", 2)]
    thermo = {r["coating"]: r["tier"] for r in out["ranking_thermo_only"]}
    assert thermo == {"Li2S": 1, "none": 3}          # ablation: reactive treated as growing
    assert "Setting:" in [u for s, u in llm.calls if "interphase_reasoner" in s][0]
    saved = json.loads((tmp_path.glob("*screen*/ranking.json").__next__()).read_text())
    assert saved["ranking"][0]["coating"] == "Li2S"


def test_screen_dry_run_builds_structures(tmp_path, toy_bulk, toy_entries):
    llm = ScriptedLLM({"interphase_reasoner": interphase_reasoner, "facet_reasoner": facets})
    m = MatchSettings(max_area=120, film_thickness=2, substrate_thickness=2, max_length_tol=0.05)
    out = run_screen(CFG, llm, settings=OrchestratorSettings(n_runs=1, match=m),
                     bulk_fn=toy_bulk, entries_fn=toy_entries, run_root=tmp_path)
    statuses = {c["status"] for r in out["ranking"] for c in r["contacts"]}
    assert statuses == {"dry_run"}


def _c(pair, rxn, character, w=None, ag=1.0):
    return ContactResult(pair=pair, reactive=rxn < -0.01, min_reaction_energy=rxn, products=[],
                         interface_type="sharp" if character == "none" else "interphase",
                         stack=list(pair), character=character, agreement=ag, w_adh=w)


def test_ranker_ordering():
    rows = [
        CoatingRow("A", [_c(("X", "A"), -0.05, "none", 0.5), _c(("A", "Y"), -0.02, "none", 0.9)]),
        CoatingRow("B", [_c(("X", "B"), -0.01, "none", 0.4), _c(("B", "Y"), 0.0, "none", 0.6)]),
        CoatingRow("C", [_c(("X", "C"), -0.30, "passivating"), _c(("C", "Y"), 0.0, "none")]),
        CoatingRow("none", [_c(("X", "Y"), -0.40, "growing")]),
    ]
    ranked = rank(rows)
    assert [r.coating for r in ranked] == ["B", "A", "C", "none"]   # tier, then smaller |ΔE_rxn|
    assert ranked[0].weakest_w_adh == 0.4
    assert "| 1 | B |" in to_markdown(ranked)
