from pathlib import Path

from benchmark.score_agreement import load_expected, score_log

YAML = Path(__file__).resolve().parents[1] / "benchmark" / "literature_cases.yaml"


def test_score_log_matches_expected():
    expected = load_expected(YAML, only_verified=False)
    log = {
        "case": "Li|Li6PS5Cl@0V",
        "events": [
            {"stage": "reactivity", "kind": "gate", "inputs": {"context": {"electrode": "Li", "electrolyte": "Li6PS5Cl"}},
             "output": {}},
            {"stage": "interface_type", "kind": "llm_decision", "inputs": {"agreement": 1.0},
             "output": {"interface_type": "interphase", "stack": ["Li", "Li2S", "Li3P", "LiCl", "Li6PS5Cl"]}},
        ],
    }
    r = score_log(log, expected)
    assert r["type_ok"] and r["order_ok"] and r["phases_j"] == 1.0


def test_score_ranking():
    from benchmark.score_agreement import score_ranking

    ranking = {"config": {"electrode": "LiCoO2", "electrolyte": "Li6PS5Cl"},
               "ranking": [{"coating": "LiNbO3", "rank": 1}, {"coating": "none", "rank": 2}],
               "ranking_thermo_only": [{"coating": "none", "rank": 1}, {"coating": "LiNbO3", "rank": 2}]}
    r = score_ranking(ranking, YAML)
    assert r["ranking"].startswith("1/1") and r["ranking_thermo_only"].startswith("0/1")
