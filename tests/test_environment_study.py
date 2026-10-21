import json
from pathlib import Path

import pytest

from interphaise.benchmark import BenchmarkQueries
from interphaise.discovery import PROMPT_VERSION, run_discovery
from scripts.analyse_environment_study import analyse, holm, mcnemar

ROOT = Path(__file__).resolve().parents[1]
POOL, BENCH = ROOT / "data/pools/mp_candidates_v2.json", ROOT / "data/benchmarks/coating_v3.json"
GOOD = "mp-aaaaajby"                    # LiCaAlF6, acceptable in v3
ACCEPTABLE = {r["candidate_id"] for r in json.loads(BENCH.read_text())["results"] if r.get("acceptable")}


def test_holm_matches_hand_computation():
    adjusted, reject = holm([0.01, 0.04, 0.03])
    assert adjusted == pytest.approx([0.03, 0.06, 0.06]) and reject == [True, False, False]
    assert holm([0.9, 0.8])[0] == [1.0, 1.0]     # 0.8 x 2 capped at 1; monotone keeps 0.9 at 1


def test_mcnemar_counts_discordant_pairs_only():
    t = mcnemar([True, True, False, False], [False, True, True, False])
    assert (t["both"], t["left_only"], t["right_only"], t["neither"], t["p"]) == (1, 1, 1, 1, 1.0)


def scripted(pick):
    def llm(system, user):
        data = json.loads(user)
        ids = [c["candidate_id"] for c in data["available"]]
        chosen = pick(ids)[: data["count"]]
        return {"proposals": [{"candidate_id": c, "hypothesis": "h", "motivation": "m", "mode": "explore"}
                              for c in chosen]}
    return llm


def test_end_to_end_on_frozen_table(tmp_path):
    d = tmp_path / "exp"
    d.mkdir()
    good_first = scripted(lambda ids: ([GOOD] if GOOD in ids else []) + [i for i in ids if i != GOOD])
    avoid_good = scripted(lambda ids: [i for i in ids if i not in ACCEPTABLE])
    arms = {"iterative": good_first, "sequential": avoid_good, "shuffled": avoid_good}
    for arm, llm in arms.items():
        for seed in (0, 1):
            state = run_discovery(BenchmarkQueries(POOL, BENCH, budget=3), strategy=arm, seed=seed, llm=llm,
                                  output=d / f"{arm}_r{seed:02d}.json")
    (d / "experiment.json").write_text(json.dumps(dict(
        arms=list(arms), repeats=2, start_seed=0, budget=3, hashes=state["hashes"], prompt_version=PROMPT_VERSION,
        benchmark="data/benchmarks/coating_v3.json", model=None, temperature=1.0, max_tokens=4096,
        allow_draft=False, benchmark_status="frozen")))
    out = analyse([d])
    env = out["environments"]["Li6PS5Cl"]
    it, seq = env["arms"]["iterative"], env["arms"]["sequential"]
    assert (it["acceptable"], seq["acceptable"]) == (2, 0)
    assert it["first_acceptable_median"] == 1 and seq["first_acceptable_mean"] == 4   # none counts as budget+1
    assert it["fluoride_fraction_early"] == 1.0          # budget 3: early half is query 1 = LiCaAlF6
    t = env["contrasts"]["iterative-sequential"]
    assert (t["left_only"], t["right_only"], t["difference"]) == (2, 0, 1.0)
    assert out["holm_family_size"] == 2 and "p_holm" in t
    assert out["aggregate_equal_weight_difference"]["iterative-sequential"] == 1.0
