"""Offline tests for the LLM-guided PET-MAD pilot (SYNC_ADEM_13 regressions included).

LiNbF6 feedback comes from Claude's real index and manifest (data/petmad/coating_comparison_v1, from
work/petmad-comparison b199608) and the genuine archived packages. Other coatings use small synthetic result packages whose energies satisfy the
W_adh arithmetic; they are fixtures, not PET-MAD results.
"""
import io
import json
import urllib.error
from pathlib import Path

import pytest

from interphaise.pilot import Blocked, Pending, Pilot, validate_decision, load_index

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "data/benchmarks/environment_v1/lco_lpscl_4v.json"
CAMPAIGN = ROOT / "data/petmad/coating_comparison_v1"
REAL_INDEX = CAMPAIGN / "index.json"
REF, TAF, CAAL, LIF = "mp-aaacjjwh", "mp-aaacjmqp", "mp-aaaaajby", "mp-aaaaabru"
K = 16.021766208
SETTINGS = dict(model="claude-haiku-5-5", temperature=1.0, max_tokens=4096)
SENTINEL = "SENTINEL-HYPOTHESIS-7781"


def package(tmp, run, w, joined):
    """Synthetic package matching the run's planned identity: W_adh arithmetic, fixed depth/count and a final
    structure whose fixed atoms carry the planned species (the rest are placeholder H atoms)."""
    import ase
    import ase.io
    d = tmp / "pkg" / run["run_id"].replace(":", "_")
    (d / "interface").mkdir(parents=True)
    area, n_atoms = run["area_A2"], run["n_atoms"]
    fixed_symbols = [el for el, n in sorted(run["fixed_species"].items()) for _ in range(n)]
    ase.io.write(d / "interface" / "final.extxyz",
                 ase.Atoms(fixed_symbols + ["H"] * (n_atoms - len(fixed_symbols)), positions=[[0, 0, i] for i in range(n_atoms)]))
    e_sub = -400.0
    e_film = w * area / K + joined - e_sub
    rel = {p: dict(converged=True, finite=True, final_energy_eV=e, max_free_force_eV_A=0.01, fmax_target_eV_A=0.05)
           for p, e in (("interface", joined), ("film", e_film), ("substrate", e_sub))}
    rel["interface"]["fixed_atom_indices"] = list(range(len(fixed_symbols)))
    (d / "result.json").write_text(json.dumps(dict(checkpoint_sha256=run["checkpoint_sha256"], numerically_valid=True,
                                                   relaxations=rel, area_A2=area, n_atoms=n_atoms, n_fixed=run["n_fixed"],
                                                   fixed_depth_A=run["fixed_rule"]["depth_A"], work_of_adhesion_J_m2=w)))
    run.update(status="valid", W_adh_J_m2=w, joined_energy_eV=joined, result_path=str(d / "result.json"),
               W_sep_J_m2=None, calculator_calls=10, wall_seconds=1.0)


def complete(tmp, index_path, cid, w_cathode, w_electrolyte):
    """Turn a candidate's pending primary rows into valid synthetic results (registry R1 lowest energy)."""
    data = json.loads(index_path.read_text())
    for r in data["runs"]:
        if r["candidate_id"] == cid and r["role"] == "primary":
            i = int(r["registry_id"][1:])
            w = (w_cathode if r["contact"] == "cathode" else w_electrolyte) - 0.05 * (i - 1)
            package(tmp, r, w, joined=-1000.0 + i)
    index_path.write_text(json.dumps(data))


class Scripted:
    """Mocked Haiku: ranks remaining IDs as given; records prompts; reports one HTTP attempt."""
    def __init__(self, bad_first=None, http=1):
        self.prompts, self.bad_first, self.http, self.last_metadata = [], bad_first, http, None

    def __call__(self, system, user):
        self.prompts.append(user)
        self.last_metadata = {"http_attempts": self.http, "returned_model": "claude-haiku-5-5"}
        data = json.loads(user)
        if self.bad_first:
            bad, self.bad_first = self.bad_first, None
            return bad
        if data["stage"] == "summary":
            return {"summary": "s", "prior_prediction_assessment": "a"}
        ids = data["unevaluated"]
        out = {"ordered_shortlist": ids, "hypothesis": SENTINEL}
        if data["stage"] != "prior":
            out.update(selected_id=ids[0], predicted_weaker_contact="electrolyte",
                       predicted_W_adh_J_m2={"cathode": [2.0, 4.0], "electrolyte": [-0.5, 1.5]},
                       change_trigger="a weak electrolyte contact", supporting_observations=["LiNbF6 electrolyte 1.63"],
                       prior_prediction_assessment="partly supported")
        return out


@pytest.fixture
def index(tmp_path):
    p = tmp_path / "index.json"
    p.write_text(REAL_INDEX.read_text())
    (tmp_path / "manifest.json").write_bytes((CAMPAIGN / "manifest.json").read_bytes())
    return p


def pilot(tmp_path, index, **kw):
    return Pilot(tmp_path / "state.json", index, TABLE, reference_id=REF, mode="mock", settings=SETTINGS, root=ROOT, **kw)


def test_real_index_and_genuine_reference_feedback(tmp_path, index):
    llm = Scripted()
    with pilot(tmp_path, index) as p:
        p.run_stage(llm)
        record = p.run_stage(llm)
    shown = json.loads(record["prompt"])["feedback"][0]
    assert shown["candidate_id"] == REF and shown["weaker_contact"] == "electrolyte"
    assert shown["contacts"]["cathode"]["W_adh_J_m2"] == pytest.approx(3.6171, abs=1e-4)
    assert shown["contacts"]["electrolyte"]["W_adh_J_m2"] == pytest.approx(1.6334, abs=1e-4)


def test_end_to_end_resume_history_and_snapshots(tmp_path, index):
    llm = Scripted()
    with pilot(tmp_path, index) as p:
        p.run_stage(llm), p.run_stage(llm)
        first_choice = p.state["selected"][0]
        with pytest.raises(Pending):
            p.run_stage(llm)                              # coating 2 physics still pending
    complete(tmp_path, index, first_choice, 2.5, 0.9)
    data = json.loads(index.read_text())                  # late change to the reference after it was revealed
    data["runs"] = [r for r in data["runs"] if not (r["candidate_id"] == REF and r["role"] == "sensitivity")]
    index.write_text(json.dumps(data))
    with pilot(tmp_path, index) as p:                    # resume
        record = p.run_stage(llm)
        assert record["stage"] == "choose_3"
        prompt = json.loads(record["prompt"])
        assert SENTINEL in json.dumps(prompt["previous_decisions"])           # its own earlier prediction
        assert prompt["previous_decisions"][-1]["predicted_W_adh_J_m2"]["electrolyte"] == [-0.5, 1.5]
        ref_snapshot = p.state["snapshots"][REF]
        assert record["feedback_sha256"][0] == ref_snapshot["sha256"]          # frozen snapshot reused
        complete(tmp_path, index, p.state["selected"][1], 3.0, 1.5)
        assert p.run_stage(llm)["stage"] == "summary" and p.state["status"] == "complete"
        rows = p.assessment()["predictions"]
    assert rows[0]["contacts"]["electrolyte"]["in_range"] is True and rows[0]["weaker_agrees"] is True


def test_altered_source_value_blocks_before_any_call(tmp_path, index):
    data = json.loads(index.read_text())
    next(r for r in data["runs"] if r["run_id"] == "mp-aaacjjwh:cathode:primary:R3")["W_adh_J_m2"] = 999.0
    index.write_text(json.dumps(data))
    llm = Scripted()
    with pilot(tmp_path, index) as p:
        p.run_stage(llm)                                  # prior has no feedback
        with pytest.raises(Blocked, match="W_adh arithmetic"):
            p.run_stage(llm)
    assert len(llm.prompts) == 1 and "999" not in llm.prompts[0]


def test_missing_planned_run_is_pending_not_dropped(tmp_path, index):
    llm = Scripted()
    with pilot(tmp_path, index) as p:                    # planned IDs frozen at start
        data = json.loads(index.read_text())
        data["runs"] = [r for r in data["runs"] if r["run_id"] != "mp-aaacjjwh:cathode:primary:R2"]
        index.write_text(json.dumps(data))
        p.run_stage(llm)
        with pytest.raises(Pending, match="missing from index"):
            p.run_stage(llm)
    assert len(llm.prompts) == 1


def test_non_comparable_registry_blocks(tmp_path, index):
    data = json.loads(index.read_text())
    r = next(r for r in data["runs"] if r["run_id"] == "mp-aaacjjwh:cathode:primary:R2")
    r["contact_build_id"] = "some-other-build"
    index.write_text(json.dumps(data))
    with pilot(tmp_path, index) as p:
        p.run_stage(Scripted())
        with pytest.raises(Blocked, match="not comparable"):
            p.run_stage(Scripted())


def _anthropic_sequence(monkeypatch, outcomes):
    """Mock urlopen: '429' raises HTTP 429, 'badjson' returns a non-JSON body."""
    from interphaise.llm import make_llm
    monkeypatch.setenv("MY_ANTHROPIC_KEY", "dummy-test-key")
    monkeypatch.setattr("time.sleep", lambda s: None)
    seq = iter(outcomes)
    def respond(request, timeout):
        kind = next(seq)
        if kind == "429":
            raise urllib.error.HTTPError(request.full_url, 429, "rate", {"request-id": "r"}, io.BytesIO(b""))
        return io.BytesIO(b"not json at all")
    monkeypatch.setattr("urllib.request.urlopen", respond)
    return make_llm("anthropic/claude-haiku-5-5", temperature=1.0, max_tokens=4096)


def test_retries_and_invalid_json_are_charged_and_stop_durably(tmp_path, index, monkeypatch):
    llm = _anthropic_sequence(monkeypatch, ["429", "429", "badjson"] * 4)
    with pilot(tmp_path, index) as p:
        assert p.run_stage(llm) is None                    # both format attempts fail
        assert p.state["http_attempts_used"] == 6 and p.state["status"] == "stopped: prior failed validation"
        assert [s["http_attempts_charged"] for s in p.state["stages"]] == [3, 3]
    with pilot(tmp_path, index) as p:                     # resume: stays stopped, nothing new is spent
        assert p.run_stage(Scripted()) is None and p.state["http_attempts_used"] == 6


def test_interrupted_calls_keep_their_reservation(tmp_path, index):
    class Crash:
        last_metadata = None
        def __call__(self, system, user):
            raise KeyboardInterrupt
    for expected in (3, 6, 9):
        with pilot(tmp_path, index) as p:
            with pytest.raises(KeyboardInterrupt):
                p.run_stage(Crash())
        assert json.loads((tmp_path / "state.json").read_text())["http_attempts_used"] == expected
    with pilot(tmp_path, index) as p:
        assert p.run_stage(Crash()) is None and p.state["status"] == "stopped: HTTP attempt cap reached"


def test_ordinary_429_then_success_is_charged_exactly(tmp_path, index, monkeypatch):
    from interphaise.llm import make_llm
    monkeypatch.setenv("MY_ANTHROPIC_KEY", "dummy-test-key")
    monkeypatch.setattr("time.sleep", lambda s: None)
    calls = iter(["429", "ok"])
    def respond(request, timeout):
        if next(calls) == "429":
            raise urllib.error.HTTPError(request.full_url, 429, "rate", {}, io.BytesIO(b""))
        ids = json.loads(json.loads(request.data)["messages"][0]["content"])["unevaluated"]
        body = {"model": "claude-haiku-5-5", "stop_reason": "end_turn", "usage": {},
                "content": [{"type": "text", "text": json.dumps({"ordered_shortlist": ids, "hypothesis": "h"})}]}
        return io.BytesIO(json.dumps(body).encode())
    monkeypatch.setattr("urllib.request.urlopen", respond)
    with pilot(tmp_path, index) as p:
        assert p.run_stage(make_llm("anthropic/claude-haiku-5-5", temperature=1.0, max_tokens=4096))["stage"] == "prior"
        assert p.state["http_attempts_used"] == 2 and p.state["http_reserved_unsettled"] == 0


def test_resume_guards(tmp_path, index):
    with pilot(tmp_path, index) as p:
        p.run_stage(Scripted())
        with pytest.raises(RuntimeError, match="another process"):
            pilot(tmp_path, index)                        # single owner of the state file
    with pytest.raises(ValueError, match="mode/settings"):
        Pilot(tmp_path / "state.json", index, TABLE, reference_id=REF, mode="live", settings=SETTINGS, root=ROOT)
    state = json.loads((tmp_path / "state.json").read_text())
    state["stages"][0]["parsed"]["hypothesis"] = "edited"
    (tmp_path / "state.json").write_text(json.dumps(state))
    with pytest.raises(ValueError, match="record hash"):
        pilot(tmp_path, index)


def test_not_run_and_consistency_rows(tmp_path, index):
    idx = load_index(index)
    statuses = {r["status"] for r in idx["runs"]}
    assert {"not_run_resource_limit", "not_run_no_admissible_construction"} <= statuses
    data = json.loads(index.read_text())
    data["runs"].append(dict(next(r for r in data["runs"] if r["candidate_id"] == REF and r["status"] == "valid"),
                             run_id="mp-aaacjjwh:cathode:consistency:G2", role="consistency", W_adh_J_m2=0.1))
    bad = dict(next(r for r in data["runs"] if r["status"] == "pending" and r["role"] == "primary"),
               status="not_run_resource_limit", failure_reason="cap")
    index.write_text(json.dumps(data))
    with pilot(tmp_path, index) as p:                    # consistency role is ignored, value never shown
        p.run_stage(Scripted()), p.run_stage(Scripted())
        assert "consistency" not in p.state["stages"][-1]["prompt"]
    data["runs"].append(dict(bad, run_id="x"))
    index.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="only for sensitivity"):
        load_index(index)


def test_decision_validation_allows_negative_ordered_intervals():
    remaining = [TAF, CAAL, LIF]
    ok = {"ordered_shortlist": remaining, "selected_id": TAF, "hypothesis": "h", "predicted_weaker_contact": "cathode",
          "predicted_W_adh_J_m2": {"cathode": [-1, 0.5], "electrolyte": [1, 3]}, "change_trigger": "t"}
    assert validate_decision("choose_2", ok, remaining)
    for change, msg in [({"selected_id": CAAL}, "first ID"),
                        ({"predicted_W_adh_J_m2": {"cathode": [3, 1], "electrolyte": [1, 3]}}, "ordered"),
                        ({"predicted_W_adh_J_m2": {"cathode": [float("nan"), 1], "electrolyte": [1, 3]}}, "finite"),
                        ({"ordered_shortlist": [TAF, CAAL]}, "exactly")]:
        with pytest.raises(ValueError, match=msg):
            validate_decision("choose_2", {**ok, **change}, remaining)
    with pytest.raises(ValueError, match="prior_prediction_assessment"):
        validate_decision("choose_3", {**ok, "supporting_observations": ["x"]}, remaining)


def test_prompt_size_bound(tmp_path, index, monkeypatch):
    import interphaise.pilot as pilot_module
    monkeypatch.setattr(pilot_module, "MAX_PROMPT_CHARS", 100)
    with pilot(tmp_path, index) as p:
        assert p.run_stage(Scripted()) is None and "exceeds" in p.state["status"]
        assert p.state["http_attempts_used"] == 0


def test_report_timeline_and_prediction_checks(tmp_path, index):
    from scripts.report_llm_petmad_pilot import plot, report
    llm = Scripted()
    with pilot(tmp_path, index) as p:
        p.run_stage(llm), p.run_stage(llm)
        complete(tmp_path, index, p.state["selected"][0], 2.5, 0.9)
        p.run_stage(llm)
        complete(tmp_path, index, p.state["selected"][1], 3.0, 1.5)
        p.run_stage(llm)
        state = p.state
    text, a = report(state)
    assert "MOCK" in text and SENTINEL in text and "## Prediction checks" in text
    assert "changed: **False**" in text and a["predictions"][0]["status"] == "revealed"
    assert plot(state, a, tmp_path / "p.png") and (tmp_path / "p.png").stat().st_size > 0
    partial = dict(state, stages=state["stages"][:2], snapshots={REF: state["snapshots"][REF]})
    text, a = report(partial)
    assert "not yet revealed" in text and "Not available" in text


def test_reference_registry_removed_before_start_is_still_required(tmp_path, index):
    data = json.loads(index.read_text())               # removed BEFORE a fresh state exists
    data["runs"] = [r for r in data["runs"] if r["run_id"] != "mp-aaacjjwh:cathode:primary:R2"]
    index.write_text(json.dumps(data))
    with pilot(tmp_path, index) as p:                    # coverage comes from the manifest, not the index
        assert "mp-aaacjjwh:cathode:primary:R2" in p.state["planned_primary"][REF]
        p.run_stage(Scripted())
        with pytest.raises(Pending, match="missing from index"):
            p.run_stage(Scripted())


def test_consistent_but_wrong_identity_is_blocked(tmp_path, index):
    data = json.loads(index.read_text())               # all cathode rows of the selected coating agree, but are wrong
    for r in data["runs"]:
        if r["candidate_id"] == TAF and r["contact"] == "cathode" and r["role"] == "primary":
            r.update(contact_build_id="wrong/build", build_sha256="0" * 64, fixed_rule={"depth_A": 5.0},
                     fixed_species={"Co": 104})
    index.write_text(json.dumps(data))
    llm = Scripted()
    with pilot(tmp_path, index) as p:
        p.run_stage(llm), p.run_stage(llm)
        assert p.state["selected"][0] == TAF
        complete(tmp_path, index, TAF, 3.5, 1.6)
        with pytest.raises(Blocked, match="differs from manifest"):
            p.run_stage(llm)


def test_saved_mask_species_must_match_manifest(tmp_path, index):
    llm = Scripted()
    with pilot(tmp_path, index) as p:
        p.run_stage(llm), p.run_stage(llm)
        complete(tmp_path, index, TAF, 3.5, 1.6)
        data = json.loads(index.read_text())
        row = next(r for r in data["runs"] if r["run_id"] == f"{TAF}:cathode:primary:R1")
        import ase.io
        final = Path(row["result_path"]).parent / "interface" / "final.extxyz"
        atoms = ase.io.read(final)
        atoms[0].symbol = "Ta"                            # one fixed atom of the wrong species
        ase.io.write(final, atoms)
        with pytest.raises(Blocked, match="fixed-atom species"):
            p.run_stage(llm)


def test_manifest_must_match_index_pin(tmp_path, index):
    (tmp_path / "manifest.json").write_text("{}")
    with pytest.raises(ValueError, match="differs from the index pin"):
        pilot(tmp_path, index)
