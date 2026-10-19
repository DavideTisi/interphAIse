from interphaise.tools.matcher import MatchSettings, enumerate_interfaces, low_index_millers
from interphaise.tools.reactivity import check_stack, interfacial_reactivity
from interphaise.tools.validation import oxidation_map, validate


def test_reactivity_closed_and_grand(toy_entries):
    e = toy_entries(None)
    rep = interfacial_reactivity("Li", "LiS2", e, voltage=0.0)
    assert rep.reactive and rep.open_element is None          # Li metal = reservoir → closed system
    assert "Li2S" in rep.most_favourable.products
    assert not interfacial_reactivity("Li", "Li2S", e, voltage=0.0).reactive
    g = interfacial_reactivity("Li2S", "LiS2", e, voltage=1.0)
    assert g.open_element == "Li"


def test_check_stack(toy_entries):
    e = toy_entries(None)
    ok, _ = check_stack(["Li", "Li2S", "LiS2"], e, voltage=0.0)
    assert ok
    ok, res = check_stack(["Li", "LiS2"], e, voltage=0.0)
    assert not ok and res[0][1].reactive


def test_matcher_and_gates(structs):
    found = enumerate_interfaces(structs["Li2S"], structs["Li"], (1, 1, 1), (1, 1, 0), ("Li2S", "Li"),
                                 MatchSettings(max_area=120, film_thickness=2, substrate_thickness=2))
    assert found
    keys = {(c.termination, c.n_atoms, round(c.area, 1)) for c, _ in found}
    assert len(keys) == len(found)                               # symmetry duplicates removed
    cand, iface = found[0]
    ok, rej, warn = validate(cand, iface, max_atoms=10, max_strain=0.04,
                             film_oxi=oxidation_map(structs["Li"]), substrate_oxi=oxidation_map(structs["Li2S"]),
                             film_formula="Li", substrate_formula="Li2S")
    assert not ok and any("too many atoms" in r for r in rej)
    assert (1, 1, 1) in low_index_millers(structs["Li2S"])


def test_oxidation_map_is_per_phase(structs):
    assert oxidation_map(structs["Li"]) == {"Li": 0.0}
    assert oxidation_map(structs["Li2S"])["Li"] == 1.0
