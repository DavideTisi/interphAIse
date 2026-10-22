"""Offline tests for the PET-MAD comparison reader. LiNbF6 uses real archived packages; other records are synthetic."""
import json
import shutil
from pathlib import Path

import pytest

from scripts.analyse_mlip_comparison import analyse

ROOT = Path(__file__).resolve().parents[1]
BATCH = ROOT / "data/petmad/niflheim_batch1"
REF, CAAL, LZP = "mp-aaacjjwh", "mp-aaaaajby", "mp-aaabevhd"


def _rel(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def real_run(contact, folder, run_id=None, base=BATCH):
    res = json.loads((base / folder / "result.json").read_text())
    sep_path = base / folder / "fixed_geometry_separation.json"
    sep = json.loads(sep_path.read_text()) if sep_path.exists() else None
    return dict(run_id=run_id or f"ref-{contact}", candidate_id=REF, contact=contact, role="primary", registry=[0, 0],
                registry_id=(run_id or f"ref-{contact}").rsplit("-", 1)[-1], contact_build_id=f"ref-{contact}-build",
                status="valid", W_adh_J_m2=res["work_of_adhesion_J_m2"], W_sep_J_m2=sep and sep["W_sep_fixed_geometry_J_m2"],
                joined_energy_eV=res["relaxations"]["interface"]["final_energy_eV"], area_A2=res["area_A2"],
                n_atoms=res["n_atoms"], checkpoint_sha256=res["checkpoint_sha256"],
                result_path=_rel(base / folder / "result.json"), separation_path=_rel(sep_path) if sep else None,
                calculator_calls=res["calculator_calls"], wall_seconds=res["wall_seconds"], reused_from="niflheim_batch1")


def write(tmp_path, runs, cohort=(REF, CAAL)):
    ckpt = runs[0]["checkpoint_sha256"]
    menu = [dict(candidate_id=c, formula=f, feasible=True) for c, f in ((REF, "LiNbF6"), (CAAL, "LiCaAlF6"), (LZP, "LiZr2(PO4)3"))]
    path = tmp_path / "index.json"
    path.write_text(json.dumps(dict(schema_version="coating_comparison_v1", checkpoint_sha256=ckpt, menu=menu,
                                    cohort=[dict(candidate_id=c, slot_reason="fixture") for c in cohort], runs=runs)))
    return path


def reference():
    return [real_run("cathode", "cathode_ref"), real_run("electrolyte", "electrolyte_seed0_ref")]


def synthetic(contact, status, ckpt, **kw):
    return dict(run_id=f"caal-{contact}-{status}", candidate_id=CAAL, contact=contact, role="primary", status=status,
                checkpoint_sha256=ckpt, failure_reason="build exceeded 1,200 atoms" if status == "failed" else None, **kw)


def test_valid_real_archive_and_compute_accounting(tmp_path):
    third = real_run("cathode", "cathode_reg_third_third", run_id="ref-cathode-third")
    out = analyse(write(tmp_path, reference() + [third], cohort=(REF,)))
    ref = out["cohort"][0]
    assert ref["contacts"]["cathode"]["status"] == "validated"
    # lowest relaxed joined energy among comparable cells selects the (1/3,1/3) registry, W_adh 3.617
    assert ref["contacts"]["cathode"]["selected_run_id"] == "ref-cathode-third"
    assert ref["contacts"]["cathode"]["W_adh_J_m2"] == pytest.approx(3.617, abs=0.001)
    assert ref["contacts"]["cathode"]["registry_range_J_m2"] == pytest.approx([3.600, 3.617], abs=0.001)
    assert ref["contacts"]["electrolyte"]["W_adh_J_m2"] == pytest.approx(1.633, abs=0.01)
    assert ref["weaker_W_adh_J_m2"] == ref["contacts"]["electrolyte"]["W_adh_J_m2"]
    assert out["invalid_runs"] == [] and out["compute"]["new"]["calls"] == 0 and out["compute"]["reused"]["calls"] > 0


def test_incomplete_campaign_and_explicit_failure_are_kept(tmp_path):
    ref = reference()
    runs = ref + [synthetic("cathode", "failed", ref[0]["checkpoint_sha256"]),
                  synthetic("electrolyte", "pending", ref[0]["checkpoint_sha256"])]
    out = analyse(write(tmp_path, runs, cohort=(REF, CAAL, LZP)))
    caal, lzp = out["cohort"][1], out["cohort"][2]
    assert caal["contacts"]["cathode"]["status"] == "failed" and caal["contacts"]["electrolyte"]["status"] == "pending"
    assert caal["weaker_W_adh_J_m2"] is None and caal["contacts"]["cathode"]["W_adh_J_m2"] is None
    assert lzp["contacts"]["cathode"]["status"] == "missing"


def test_duplicate_run_ids_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="duplicate run_id"):
        analyse(write(tmp_path, reference() + [reference()[0]]))


def _copy(tmp_path, folder, edit):
    dst = tmp_path / "pkg" / folder
    shutil.copytree(BATCH / folder, dst)
    res = json.loads((dst / "result.json").read_text())
    edit(res)
    (dst / "result.json").write_text(json.dumps(res))
    return tmp_path / "pkg"


@pytest.mark.parametrize("edit,expect", [
    (lambda r: r["relaxations"]["interface"].update(converged=False), "not converged"),
    (lambda r: r.update(checkpoint_sha256="other"), "checkpoint"),
    (lambda r: r.update(area_A2=r["area_A2"] * 1.01), "area differs"),
])
def test_unconverged_wrong_checkpoint_and_area_mismatch_invalidate(tmp_path, edit, expect):
    base = _copy(tmp_path, "cathode_ref", edit)
    runs = [real_run("cathode", "cathode_ref", base=BATCH), real_run("electrolyte", "electrolyte_seed0_ref")]
    runs[0]["result_path"] = str(base / "cathode_ref" / "result.json")
    out = analyse(write(tmp_path, runs, cohort=(REF,)))
    assert out["cohort"][0]["contacts"]["cathode"]["status"] == "invalid evidence"   # integrity, not a calculation failure
    assert any(expect in p for p in out["invalid_runs"][0]["problems"])


def test_energy_arithmetic_mismatch_invalidates(tmp_path):
    runs = reference()
    runs[0]["W_adh_J_m2"] += 0.1
    out = analyse(write(tmp_path, runs, cohort=(REF,)))
    assert any("W_adh arithmetic" in p for p in out["invalid_runs"][0]["problems"])
