"""Offline tests for the LLM-guided PET-MAD pilot runner. All energies below are synthetic fixtures."""
import json
from pathlib import Path

import pytest

from interphaise.pilot import Pending, Pilot, feedback_bundle, load_index, validate_decision

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "data/benchmarks/environment_v1/lco_lpscl_4v.json"
REF, CAAL, LZP, LIF, TAF = "mp-aaacjjwh", "mp-aaaaajby", "mp-aaabevhd", "mp-aaaaabru", "mp-aaacjmqp"
FORMULA = {REF: "LiNbF6", CAAL: "LiCaAlF6", LZP: "LiZr2(PO4)3", LIF: "LiF", TAF: "LiTaF6"}
CKPT = "fixture-checkpoint"
SECRET = 7.777  # synthetic W_adh of a candidate that is never revealed before its own decision


def run(cid, contact, i, w, status="valid", role="primary"):
    return dict(run_id=f"{cid}-{contact}-{role}-{i}", candidate_id=cid, contact=contact, role=role,
                sensitivity_kind="thickness" if role == "sensitivity" else None, registry=[i / 3, 0.0],
                status=status, W_adh_J_m2=w if status == "valid" else None, W_sep_J_m2=(w + 1) if status == "valid" else None,
                joined_energy_eV=-100.0 - i if status == "valid" else None, checkpoint_sha256=CKPT,
                failure_reason=None if status != "failed" else "relaxation step limit", calculator_calls=10, wall_seconds=5.0)


def write_index(path, runs):
    path.write_text(json.dumps(dict(schema_version="coating_comparison_v1", checkpoint_sha256=CKPT,
                                    menu=[dict(candidate_id=c, formula=f, feasible=True, limitations=["fixture"])
                                          for c, f in FORMULA.items()], runs=runs)))


def reference_runs():
    return [run(REF, "cathode", 0, 3.6), run(REF, "cathode", 1, 3.5), run(REF, "electrolyte", 0, 1.6),
            run(REF, "electrolyte", 1, 1.4, role="sensitivity")]


class Scripted:
    """Mocked Haiku: picks the first two remaining IDs; records prompts; reports one HTTP attempt."""
    def __init__(self, bad_first=None, http=1):
        self.prompts, self.bad_first, self.http = [], bad_first, http
        self.last_metadata = None

    def __call__(self, system, user):
        self.prompts.append(user)
        self.last_metadata = {"http_attempts": self.http, "returned_model": "claude-haiku-5-5"}
        data = json.loads(user)
        if self.bad_first:
            bad, self.bad_first = self.bad_first, None
            return bad
        if data["stage"] == "summary":
            return {"summary": "fixture summary"}
        ids = data["unevaluated"]
        out = {"ordered_shortlist": ids, "hypothesis": "fixture hypothesis"}
        if data["stage"] != "prior":
            out.update(selected_id=ids[0], predicted_weaker_contact="electrolyte",
                       predicted_W_adh_J_m2={"cathode": [2.0, 4.0], "electrolyte": [1.0, 2.0]},
                       change_trigger="a weak electrolyte contact", supporting_observations=["reference electrolyte 1.6"])
        return out


@pytest.fixture
def files(tmp_path):
    index = tmp_path / "index.json"
    write_index(index, reference_runs() + [run(LIF, "cathode", 0, SECRET), run(LIF, "electrolyte", 0, SECRET)])
    return tmp_path / "state.json", index


def test_end_to_end_with_pending_and_resume(files):
    state, index = files
    llm = Scripted()
    pilot = Pilot(state, index, TABLE, reference_id=REF)
    assert pilot.run_stage(llm)["stage"] == "prior"
    choose2 = pilot.run_stage(llm)
    assert choose2["stage"] == "choose_2" and pilot.state["selected"] == [CAAL]
    with pytest.raises(Pending):                       # coating 2 physics not available yet
        pilot.run_stage(llm)
    data = json.loads(index.read_text())
    data["runs"] += [run(CAAL, "cathode", 0, 2.5), run(CAAL, "electrolyte", 0, 0.9)]
    index.write_text(json.dumps(data))
    pilot = Pilot(state, index, TABLE, reference_id=REF)   # resume from the saved state
    assert pilot.run_stage(llm)["stage"] == "choose_3" and pilot.state["selected"] == [CAAL, LZP]
    data["runs"] += [run(LZP, "cathode", 0, 3.0), run(LZP, "electrolyte", 0, 1.5)]
    index.write_text(json.dumps(data))
    assert pilot.run_stage(llm)["stage"] == "summary" and pilot.state["status"] == "complete"
    report = pilot.assessment()
    first = report["predictions"][0]
    assert first["candidate_id"] == CAAL and first["contacts"]["electrolyte"]["in_range"] is False
    assert first["contacts"]["electrolyte"]["miss"] == pytest.approx(0.1) and first["weaker_agrees"] is True
    assert report["decision_comparison"] == dict(initial_next=LZP, chosen=LZP, changed=False,
                                                 note=report["decision_comparison"]["note"])
    assert report["http_attempts_used"] == 4
    assert all(s.get("record_sha256") for s in pilot.state["stages"])


def test_no_unrevealed_results_or_sensitivity_values_in_prompts(files):
    state, index = files
    llm = Scripted()
    pilot = Pilot(state, index, TABLE, reference_id=REF)
    pilot.run_stage(llm), pilot.run_stage(llm)
    for prompt in llm.prompts:
        assert str(SECRET) not in prompt               # LiF results exist but were never revealed
        assert '"W_adh_J_m2": 1.4' not in prompt       # sensitivity value withheld, only "pending" shown
    assert '"status": "pending"' in llm.prompts[-1]


@pytest.mark.parametrize("bad", [
    {"ordered_shortlist": ["mp-not-in-menu"], "hypothesis": "h"},
    {"ordered_shortlist": [CAAL, CAAL, LZP, LIF, TAF], "hypothesis": "h"},
])
def test_invalid_prior_is_charged_and_retried(files, bad):
    state, index = files
    llm = Scripted(bad_first=bad)
    pilot = Pilot(state, index, TABLE, reference_id=REF)
    record = pilot.run_stage(llm)
    assert record["stage"] == "prior" and record["attempt"] == 1
    assert pilot.state["http_attempts_used"] == 2 and "error" in pilot.state["stages"][0]


def test_decision_validation_rules():
    remaining = [CAAL, LZP, LIF]
    ok = {"ordered_shortlist": remaining, "selected_id": CAAL, "hypothesis": "h", "predicted_weaker_contact": "cathode",
          "predicted_W_adh_J_m2": {"cathode": [1, 2], "electrolyte": [1, 3]}, "change_trigger": "t"}
    assert validate_decision("choose_2", ok, remaining)
    for change, msg in [({"selected_id": LZP}, "first ID"), ({"predicted_W_adh_J_m2": {"cathode": [3, 1], "electrolyte": [1, 3]}}, "low <= high"),
                        ({"predicted_weaker_contact": "both"}, "weaker"), ({"ordered_shortlist": [CAAL, LZP]}, "exactly")]:
        with pytest.raises(ValueError, match=msg):
            validate_decision("choose_2", {**ok, **change}, remaining)
    with pytest.raises(ValueError, match="supporting_observations"):
        validate_decision("choose_3", ok, remaining)


def test_failed_contact_consumes_the_slot(files, tmp_path):
    state, index = files
    data = json.loads(index.read_text())
    data["runs"] += [run(CAAL, "cathode", 0, None, status="failed"), run(CAAL, "electrolyte", 0, 0.9)]
    index.write_text(json.dumps(data))
    bundle = feedback_bundle(load_index(index), json.loads(TABLE.read_text()), CAAL)
    assert bundle["contacts"]["cathode"]["status"] == "failed" and bundle["min_W_adh_J_m2"] is None
    assert bundle["weaker_contact"] == "unresolved"


def test_http_cap_is_a_hard_ceiling(files):
    state, index = files
    data = json.loads(index.read_text())
    data["runs"] += [run(CAAL, "cathode", 0, 2.5), run(CAAL, "electrolyte", 0, 0.9),
                     run(LZP, "cathode", 0, 3.0), run(LZP, "electrolyte", 0, 1.5)]
    index.write_text(json.dumps(data))
    llm = Scripted(http=3)                             # every call used its worst case: 3 HTTP attempts
    pilot = Pilot(state, index, TABLE, reference_id=REF, http_cap=10, max_http_per_call=3)
    for _ in range(4):
        pilot.run_stage(llm)
    assert pilot.state["http_attempts_used"] == 9      # prior, choose_2, choose_3; summary refused (9 + 3 > 10)
    assert pilot.state["status"] == "stopped: HTTP attempt cap reached" and len(llm.prompts) == 3


def test_index_validation_rejects_bad_records(tmp_path):
    index = tmp_path / "index.json"
    bad = reference_runs() + [reference_runs()[0]]                                     # duplicate run_id
    write_index(index, bad)
    with pytest.raises(ValueError, match="duplicate run_id"):
        load_index(index)
    r = run(CAAL, "cathode", 0, 2.0); r["checkpoint_sha256"] = "other"
    write_index(index, reference_runs() + [r])
    with pytest.raises(ValueError, match="checkpoint"):
        load_index(index)


def test_small_menu_is_refused_without_override(tmp_path):
    index = tmp_path / "index.json"
    write_index(index, reference_runs())
    data = json.loads(index.read_text())
    for c in data["menu"][2:]:
        c["feasible"] = False
    index.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="report before live calls"):
        Pilot(tmp_path / "s.json", index, TABLE, reference_id=REF)
