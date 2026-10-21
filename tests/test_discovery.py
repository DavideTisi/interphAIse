import json
from itertools import permutations
from pathlib import Path

import pytest

from interphaise.benchmark import BenchmarkQueries
from interphaise.discovery import FEEDBACK_FIELDS, random_success_curve, run_discovery, write_synthetic_benchmark

ROOT = Path(__file__).resolve().parents[1]
POOL, BENCH = ROOT / "data/pools/mp_candidates_v2.json", ROOT / "data/benchmarks/coating_v3.json"
TABLE = {r["candidate_id"]: r for r in json.loads(BENCH.read_text())["results"]}
FAILED = next(c for c, r in TABLE.items() if r["status"] != "ok")


def queries(budget=3):
    return BenchmarkQueries(POOL, BENCH, budget=budget)


def P(cid):
    return {"candidate_id": cid, "hypothesis": "chemistry", "motivation": "none", "mode": "explore"}


def first_available(calls):
    def llm(system, user):
        data = json.loads(user)
        calls.append(user)
        return {"proposals": [P(data["available"][0]["candidate_id"])]}
    return llm


def test_iterative_sees_only_queried_outcomes_without_provenance():
    calls = []
    state = run_discovery(queries(), strategy="iterative", llm=first_available(calls))
    assert len(state["history"]) == 3 and state["status"] == "complete"
    shown = json.loads(calls[2])["evaluated"]
    assert [h["proposal"]["candidate_id"] for h in shown] == [h["proposal"]["candidate_id"] for h in state["history"][:2]]
    assert "penalty_bin" in shown[0]["result"]
    for user in calls:
        for leak in ("evaluation_wall_seconds", "entries", "endpoint_decomposition", "absolute_contact", "mu_Li"):
            assert leak not in user
    assert all(set(h["result"]) <= set(FEEDBACK_FIELDS) for h in shown)


def test_sequential_sees_choices_but_no_outcomes():
    calls = []
    state = run_discovery(queries(), strategy="sequential", llm=first_available(calls))
    later = json.loads(calls[2])
    assert [h["proposal"]["candidate_id"] for h in later["evaluated"]] == \
           [h["proposal"]["candidate_id"] for h in state["history"][:2]]
    for user in calls:
        assert all(set(h) == {"proposal"} for h in json.loads(user)["evaluated"])
        for h in state["history"]:
            if "penalty" in h["result"]:
                assert repr(h["result"]["penalty"]) not in user


def test_failed_query_consumes_budget_and_stays_hidden_from_sequential():
    calls = []
    def llm(system, user):
        calls.append(user)
        data = json.loads(user)
        ids = [c["candidate_id"] for c in data["available"]]
        return {"proposals": [P(FAILED if FAILED in ids else ids[0])]}
    state = run_discovery(queries(2), strategy="sequential", llm=llm)
    assert state["history"][0]["result"]["status"] == "failed"
    assert len(state["history"]) == 2 and state["trace"][0]["best_candidate_id"] is None
    assert json.loads(calls[1])["evaluated"] == [{"proposal": state["history"][0]["proposal"]}]
    assert TABLE[FAILED]["error"] not in calls[1]


def test_upfront_one_call_before_any_query():
    calls = []
    def llm(system, user):
        data = json.loads(user)
        calls.append(data)
        assert data["evaluated"] == []
        return {"proposals": [P(c["candidate_id"]) for c in data["available"][:3]]}
    state = run_discovery(queries(), strategy="upfront", llm=llm)
    assert len(calls) == 1 and len(state["history"]) == 3


def test_malformed_messages_bounded_retries_without_evaluation(tmp_path):
    q = queries()
    out = tmp_path / "run.json"
    with pytest.raises(ValueError, match="exhausted"):
        run_discovery(q, strategy="iterative", llm=lambda *_: {"proposals": []},
                      output=out, max_proposal_attempts=2)
    saved = json.loads(out.read_text())
    assert saved["status"] == "failed" and len(saved["proposal_attempts"]) == 2
    assert q.remaining == 3


@pytest.mark.parametrize('bad_id', ['mp-not-in-pool', None, ['invalid']])
def test_invalid_id_is_charged_and_does_not_trigger_free_repair(bad_id):
    q = queries(2)
    state = run_discovery(q, strategy='iterative', llm=lambda *_: {'proposals': [P(bad_id)]})
    assert q.remaining == 0
    assert len(state['proposal_attempts']) == len(state['history']) == 2
    assert all(h['result']['status'] == 'failed' for h in state['history'])


def test_repeated_id_in_upfront_list_costs_an_evaluation():
    q = queries(2)
    cid = q.available()[0]['candidate_id']
    state = run_discovery(q, strategy='upfront', llm=lambda *_: {'proposals': [P(cid), P(cid)]})
    assert q.remaining == 0
    assert state['history'][1]['result']['error'] == 'Candidate already queried'
    assert len(state['proposal_attempts']) == 1


def test_proposal_without_mode_or_repeat_is_repaired():
    first = queries().available()[0]["candidate_id"]
    responses = iter([{"candidate_id": first, "hypothesis": "chemistry"}, P(first)])
    state = run_discovery(queries(1), strategy="iterative", llm=lambda *_: {"proposals": [next(responses)]})
    assert "mode" in state["proposal_attempts"][0]["error"]
    assert state["history"][0]["proposal"]["mode"] == "explore"


def test_random_reproducible_and_order_paired_with_llm_arms():
    a = run_discovery(queries(), strategy="random", seed=7)
    b = run_discovery(queries(), strategy="random", seed=7)
    ids = lambda s: [h["proposal"]["candidate_id"] for h in s["history"]]
    assert ids(a) == ids(b) and len(set(ids(a))) == 3
    calls = []
    run_discovery(queries(), strategy="sequential", seed=7, llm=first_available(calls))
    assert [c["candidate_id"] for c in json.loads(calls[0])["available"][:3]] == ids(a)


def test_run_records_hashes_and_prompt_version():
    state = run_discovery(queries(), strategy="random")
    assert state["hashes"]["benchmark_sha256"] == json.loads(BENCH.read_text())["sha256"]
    assert state["prompt_version"]


def test_random_curve_matches_enumeration_and_handoff_numbers():
    pool, good = range(6), {1, 4}
    orders = list(permutations(pool))
    for k, p in enumerate(random_success_curve(6, 2, 6), start=1):
        assert p == pytest.approx(sum(bool(good & set(o[:k])) for o in orders) / len(orders))
    assert random_success_curve(50, 2, 10)[-1] == pytest.approx(0.363265, abs=1e-6)
    assert random_success_curve(50, 1, 10)[-1] == pytest.approx(0.2)


def test_synthetic_benchmark_runs_through_real_query_boundary(tmp_path):
    pool, bench = write_synthetic_benchmark(tmp_path, seed=3)
    with pytest.raises(ValueError, match="Draft"):
        BenchmarkQueries(pool, bench, budget=5)
    state = run_discovery(BenchmarkQueries(pool, bench, budget=5, allow_draft=True), strategy="random", seed=1)
    assert len(state["history"]) == 5
    assert write_synthetic_benchmark(tmp_path / "again", seed=3)[1].read_text() == bench.read_text()
