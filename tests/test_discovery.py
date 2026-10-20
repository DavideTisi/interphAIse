import json

import pytest

from interphaise.discovery import Evaluation, quality, run_discovery
from interphaise.screen import ScreenConfig

CFG = ScreenConfig("LiCoO2", "Li6PS5Cl", ["LiNbO3", "Li3PO4", "LiTaO3"])


def test_iterative_feedback_and_no_future_outcomes(tmp_path):
    calls = []
    def llm(system, user):
        data = json.loads(user)
        calls.append(data)
        return {"proposals": [{"coating": data["available"][0], "hypothesis": "test chemistry"}]}
    def evaluate(c):
        return Evaluation(c, "ok", -0.2 if c == "LiNbO3" else -0.1)
    out = tmp_path / "discovery.json"
    state = run_discovery(CFG, evaluate, budget=2, llm=llm, output=out)
    assert calls[0]["evaluated"] == []
    assert len(calls[1]["evaluated"]) == 1
    assert calls[1]["evaluated"][0]["result"]["worst_reaction_energy"] == -0.2
    assert "LiNbO3" not in calls[1]["available"]
    assert state["trace"][-1]["best"]["coating"] == "Li3PO4"
    assert json.loads(out.read_text())["status"] == "complete"


def test_upfront_one_call_before_any_evaluation():
    events = []
    def llm(system, user):
        events.append("proposal")
        assert json.loads(user)["evaluated"] == []
        return {"proposals": [{"coating": c, "hypothesis": "chemistry"} for c in CFG.coatings[:2]]}
    def evaluate(c):
        events.append(c)
        return Evaluation(c, "ok", -0.1)
    run_discovery(CFG, evaluate, budget=2, strategy="upfront", llm=llm)
    assert events == ["proposal", *CFG.coatings[:2]]


def test_failures_consume_budget_and_do_not_win():
    def evaluate(c):
        if c == CFG.coatings[0]:
            raise RuntimeError("calculation failed")
        return Evaluation(c, "ok", -0.4)
    state = run_discovery(CFG, evaluate, budget=2, strategy="fixed")
    assert len(state["history"]) == 2
    assert state["history"][0]["result"]["status"] == "failed"
    assert state["trace"][0]["best"] is None
    assert state["trace"][1]["best"]["coating"] == CFG.coatings[1]


def test_invalid_proposals_bounded_and_checkpointed(tmp_path):
    def llm(*_):
        return {"proposals": [{"coating": "not in pool", "hypothesis": "test"}]}
    def evaluate(c):
        pytest.fail("Invalid proposal must not run a calculation")
    out = tmp_path / "discovery.json"
    with pytest.raises(ValueError, match="exhausted"):
        run_discovery(CFG, evaluate, llm=llm, output=out, max_proposal_attempts=2)
    state = json.loads(out.read_text())
    assert state["status"] == "failed"
    assert len(state["proposal_attempts"]) == 2
    assert state["history"] == []


def test_fixed_objective_and_missing_adhesion():
    assert quality(Evaluation("A", "ok", -0.01, 0.1)) > quality(Evaluation("B", "ok", -0.2, 4.0))
    assert quality(Evaluation("A", "ok", -0.1, 2.0)) > quality(Evaluation("B", "ok", -0.1, 1.0))
    assert not quality(Evaluation("A", "ok", -0.1), require_adhesion=True)[0]
    assert not quality(Evaluation("A", "ok", float("nan")))[0]


def test_random_reproducible_and_no_repeats():
    evaluate = lambda c: Evaluation(c, "ok", -0.1)
    a = run_discovery(CFG, evaluate, strategy="random", seed=7)
    b = run_discovery(CFG, evaluate, strategy="random", seed=7)
    order = lambda s: [h["result"]["coating"] for h in s["history"]]
    assert order(a) == order(b)
    assert len(set(order(a))) == 3


def test_live_thermodynamic_adapter(monkeypatch, toy_bulk, toy_entries):
    from interphaise.discovery import CoatingEvaluator
    from interphaise.tools import materials
    monkeypatch.setattr(materials, "get_bulk", toy_bulk)
    monkeypatch.setattr(materials, "get_entries", toy_entries)
    cfg = ScreenConfig("Li", "LiS2", ["Li2S"], voltage=0, role="anode")
    result = CoatingEvaluator(cfg)("Li2S")
    assert result.status == "ok"
    assert len(result.details["contacts"]) == 2
    assert result.worst_reaction_energy >= -1e-8


def test_full_adapter_rejects_partial_contact_failure(monkeypatch):
    from interphaise.discovery import CoatingEvaluator
    from interphaise import screen
    monkeypatch.setattr(screen, "run_screen", lambda *a, **k: {
        "ranking": [{"contacts": [{"status": "ok"}, {"status": "failed"}],
                     "worst_reaction_energy": 0., "weakest_w_adh": None}], "run_dir": "test"})
    result = CoatingEvaluator(CFG, calc=object())(CFG.coatings[0])
    assert result.status == "failed"
    assert not quality(result, True)[0]


def test_repeated_candidate_rejected_then_repaired():
    responses = iter(["LiNbO3", "LiNbO3", "Li3PO4"])
    def llm(*_):
        return {"proposals": [{"coating": next(responses), "hypothesis": "chemistry"}]}
    state = run_discovery(CFG, lambda c: Evaluation(c, "ok", -0.1), budget=2, llm=llm)
    assert len(state["proposal_attempts"]) == 3
    assert len(state["history"]) == 2
    assert "error" in state["proposal_attempts"][1]


def test_budget_validation_precedes_evaluation():
    with pytest.raises(ValueError, match="Budget"):
        run_discovery(CFG, lambda c: pytest.fail("must not evaluate"), budget=4, strategy="random")
