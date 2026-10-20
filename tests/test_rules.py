"""Rules arm: each deterministic decision, then the full pipeline with RulesPolicy."""

import json

from interphaise.context import Candidate, EnergeticsResult, InterfaceContext
from interphaise.llm import ScriptedLLM
from interphaise.orchestrator import Orchestrator, OrchestratorSettings
from interphaise.policies import LLMPolicy, RuleSettings, RulesPolicy, as_policy, bfdh_ranking
from interphaise.screen import ScreenConfig, run_screen
from interphaise.tools.matcher import MatchSettings
from interphaise.tools.mlip import load_mlip
from interphaise.tools.reactivity import interfacial_reactivity

INSULATOR = lambda f: 3.0  # noqa: E731
METAL = lambda f: 0.0  # noqa: E731


def ctx(electrolyte="LiS2"):
    return InterfaceContext(electrode="Li", electrolyte=electrolyte, role="anode", voltage=0.0, max_strain=0.05)


# ---------------------------------------------------------------- decision 1


def test_reactive_pair_gives_ordered_passivating_interphase(toy_entries):
    e = toy_entries(None)
    rep = interfacial_reactivity("Li", "LiS2", e, voltage=0.0)
    d, agree, _ = RulesPolicy(band_gap_fn=INSULATOR).decide_interface_type(ctx(), rep, e)
    assert d.interface_type == "interphase" and d.stack == ["Li", "Li2S", "LiS2"]
    assert d.character == "passivating" and agree == 1.0
    assert "rule:" in d.rationale


def test_metallic_product_means_growing(toy_entries):
    e = toy_entries(None)
    rep = interfacial_reactivity("Li", "LiS2", e, voltage=0.0)
    d, _, _ = RulesPolicy(band_gap_fn=METAL).decide_interface_type(ctx(), rep, e)
    assert d.character == "growing"


def test_stable_or_weakly_reactive_pair_is_sharp(toy_entries):
    e = toy_entries(None)
    rep = interfacial_reactivity("Li", "Li2S", e, voltage=0.0)
    d, _, _ = RulesPolicy(band_gap_fn=INSULATOR).decide_interface_type(ctx("Li2S"), rep, e)
    assert d.interface_type == "sharp" and d.character == "none"
    # threshold below the reaction energy → the reactive pair is also called sharp
    rep2 = interfacial_reactivity("Li", "LiS2", e, voltage=0.0)
    lax = RulesPolicy(RuleSettings(sharp_threshold=rep2.min_reaction_energy - 1.0), band_gap_fn=INSULATOR)
    assert lax.decide_interface_type(ctx(), rep2, e)[0].interface_type == "sharp"


# ---------------------------------------------------------------- decision 2


def test_bfdh_handles_systematic_absences(structs):
    # bcc Li: (100) is extinct (effective d = a/2), so (110) leads
    assert bfdh_ranking(structs["Li"])[0][0] == (1, 1, 0)
    # fcc-based Li2S: (111) leads (d = a/√3 > a/2 for the extinct (100))
    assert bfdh_ranking(structs["Li2S"])[0][0] == (1, 1, 1)


def test_rules_facets_skip_tried_pairs(structs):
    pol = RulesPolicy(band_gap_fn=INSULATOR)
    first = pol.propose_facets("Li", "Li2S", structs["Li"], structs["Li2S"], "", 3)
    assert first[0][0].substrate_miller == (1, 1, 0) and first[0][0].film_miller == (1, 1, 1)
    tried = {(c.substrate_miller, c.film_miller) for c, _ in first}
    again = pol.propose_facets("Li", "Li2S", structs["Li"], structs["Li2S"], "", 3, tried=tried)
    assert again and not ({(c.substrate_miller, c.film_miller) for c, _ in again} & tried)


# ---------------------------------------------------------------- decision 3


def _res(w=0.5):
    cand = Candidate(pair=("A", "B"), film_miller=(1, 0, 0), substrate_miller=(1, 0, 0), termination=("a", "b"),
                     n_atoms=100, area=50.0, von_mises_strain=0.01)
    return EnergeticsResult(candidate=cand, best_offset=(0, 0), best_gap=2.0, e_interface=0, e_film=0,
                            e_substrate=0, w_adh=w)


CLEAN = {"n_atoms": 100, "min_distance_after_A": 2.0, "gap_before_A": 2.0, "gap_after_A": 2.1,
         "film_atoms_penetrating_substrate": 0, "substrate_atoms_penetrating_film": 0,
         "mean_displacement_interface_region_A": 0.2, "mean_CN_interface_region_before": 6.0,
         "mean_CN_interface_region_after": 6.2}


def test_judge_rules():
    pol = RulesPolicy(band_gap_fn=INSULATOR)
    assert pol.judge(_res(), CLEAN, [])[0].verdict == "accept"
    assert pol.judge(_res(), CLEAN, ["film slab is polar"])[0].verdict == "accept_with_caveat"
    v, _ = pol.judge(_res(), {**CLEAN, "gap_after_A": 5.0}, [])
    assert (v.verdict, v.action) == ("reject", "next_termination")
    v, _ = pol.judge(_res(), {**CLEAN, "film_atoms_penetrating_substrate": 10}, [])
    assert (v.verdict, v.action) == ("reject", "different_facets")
    v, _ = pol.judge(_res(), {**CLEAN, "mean_displacement_interface_region_A": 2.0}, [])
    assert (v.verdict, v.action) == ("reject", "thicker_slabs")
    assert pol.judge(_res(w=-0.1), CLEAN, [])[0].action == "next_termination"


# ---------------------------------------------------------------- wiring


def test_as_policy_wraps_bare_llm():
    p = as_policy(ScriptedLLM({}), n_runs=2)
    assert isinstance(p, LLMPolicy) and p.name == "llm" and p.n_runs == 2
    r = RulesPolicy(band_gap_fn=INSULATOR)
    assert as_policy(r) is r


def test_full_pipeline_with_rules(tmp_path, toy_bulk, toy_entries):
    m = MatchSettings(max_area=120, film_thickness=2, substrate_thickness=2, max_length_tol=0.05)
    s = OrchestratorSettings(max_retries=1, top_k_candidates=1, registry_n_xy=2, registry_gaps=(2.0,), steps=10,
                             match=m)
    loose = RuleSettings(max_interface_displacement=99, max_cn_change=99, max_gap_opening=99,
                         max_penetration_fraction=1.0)  # LJ toy relaxes wildly; test the plumbing only
    out = Orchestrator(ctx(), RulesPolicy(loose, band_gap_fn=INSULATOR), calc=load_mlip("lj"), settings=s,
                       bulk_fn=toy_bulk, entries_fn=toy_entries, run_root=tmp_path).run()
    assert out["policy"] == "rules"
    assert out["decision"].stack == ["Li", "Li2S", "LiS2"]
    assert [p["status"] for p in out["pairs"]] == ["ok", "ok"]
    log = json.loads(next(tmp_path.glob("*/decision_log.json")).read_text())
    decisions = [e for e in log["events"] if e["kind"] == "decision"]
    assert decisions and all(e["inputs"]["policy"] == "rules" for e in decisions)


def test_screen_with_rules_and_compare(tmp_path, toy_bulk, toy_entries):
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from compare_arms import compare, latest_per_arm

    cfg = ScreenConfig(electrode="Li", electrolyte="LiS2", coatings=["Li2S"], voltage=0.0, role="anode",
                       max_strain=0.05)
    s = OrchestratorSettings(build_structures=False)
    rules = run_screen(cfg, RulesPolicy(band_gap_fn=INSULATOR), settings=s, bulk_fn=toy_bulk,
                       entries_fn=toy_entries, run_root=tmp_path)
    assert rules["policy"] == "rules" and rules["policy_settings"]["sharp_threshold"] == -0.05
    assert [(r["coating"], r["tier"]) for r in rules["ranking"]] == [("Li2S", 1), ("none", 2)]

    # an "LLM" arm that calls the bare contact sharp: one override
    llm = ScriptedLLM({"interphase_reasoner": {"interface_type": "sharp", "stack": [], "character": "none"}})
    run_screen(cfg, llm, settings=OrchestratorSettings(n_runs=1, build_structures=False), bulk_fn=toy_bulk,
               entries_fn=toy_entries, run_root=tmp_path)
    arms = latest_per_arm(tmp_path)
    assert set(arms) == {"rules", "llm"}
    md = compare(arms, Path(__file__).resolve().parents[1] / "benchmark" / "literature_cases.yaml")
    assert "LLM overrides the rules on 1/3 contacts" in md
