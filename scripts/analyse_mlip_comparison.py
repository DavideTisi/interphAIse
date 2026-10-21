"""Validate a PET-MAD coating-comparison campaign and produce its table and figure (SYNC_ADEM_11 §2–3).

    python scripts/analyse_mlip_comparison.py --index data/petmad/coating_comparison_v1/index.json \
        --out data/petmad/coating_comparison_v1/analysis

Reads the campaign index (contract: data/experiments/llm_petmad_pilot_v1/CONTRACT.md), never globs runs.
Every valid run is re-checked against its source files: checkpoint, convergence/force targets, finite
energies, W_adh = (E_film + E_substrate - E_interface)/A and, when present, the rigid-separation W_sep.
Runs that fail a check become invalid with reasons; nothing is dropped and missing work is never zero.
Registry selection is the frozen lowest-relaxed-joined-energy rule within one comparable cell (same area
and atom count); total energies are never compared between coatings or bulk seeds. Sensitivity results
are finite tested differences from the selected primary, not confidence intervals. Thermodynamic values
are joined by exact material ID from the frozen sulfide table. No combined score, no adhesion threshold.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from interphaise.pilot import CONTACTS, load_index, thermo_card

EV_A2_TO_J_M2 = 16.021766208
SULFIDE_TABLE = ROOT / "data/benchmarks/environment_v1/lco_lpscl_4v.json"
SULFIDE_SHA = "f70342c9aae0bd0e95f588bfb8c2f956815b3cf336c24e866119f7ab7f45f510"
TOL_J_M2 = 1e-6


def _resolve(path):
    p = Path(path)
    return p if p.is_absolute() else ROOT / p


def source_problems(run, checkpoint):
    """Re-check one 'valid' run against its result package; [] means the work is validated."""
    problems = []
    if not run.get("result_path") or not _resolve(run["result_path"]).exists():
        return ["result file missing"]
    raw = _resolve(run["result_path"]).read_bytes()
    if run.get("result_sha256") and hashlib.sha256(raw).hexdigest() != run["result_sha256"]:
        problems.append("result file hash differs from index")
    res = json.loads(raw)
    if res.get("checkpoint_sha256") != checkpoint:
        problems.append("result checkpoint differs from campaign")
    if res.get("numerically_valid") is not True:
        problems.append("result not numerically_valid")
    rel = res.get("relaxations", {})
    for part in ("interface", "film", "substrate"):
        r = rel.get(part, {})
        if not (r.get("converged") and r.get("finite") and math.isfinite(r.get("final_energy_eV", math.nan))):
            problems.append(f"{part} relaxation not converged/finite")
        elif not r.get("max_free_force_eV_A", math.inf) <= r.get("fmax_target_eV_A", -math.inf):
            problems.append(f"{part} free force above target")
    area = res.get("area_A2")
    if not (isinstance(area, (int, float)) and area > 0):
        return problems + ["invalid area"]
    if run.get("area_A2") is not None and abs(run["area_A2"] - area) > 1e-6:
        problems.append("area differs from index")
    if run.get("n_atoms") is not None and run["n_atoms"] != res.get("n_atoms"):
        problems.append("atom count differs from index")
    if not problems:
        e = {p: rel[p]["final_energy_eV"] for p in ("interface", "film", "substrate")}
        w = (e["film"] + e["substrate"] - e["interface"]) / area * EV_A2_TO_J_M2
        if abs(w - run["W_adh_J_m2"]) > TOL_J_M2 or abs(w - res.get("work_of_adhesion_J_m2", math.nan)) > TOL_J_M2:
            problems.append(f"W_adh arithmetic mismatch (recomputed {w:.6f})")
        if abs(e["interface"] - run["joined_energy_eV"]) > 1e-6:
            problems.append("joined energy differs from interface final energy")
        if run.get("W_sep_J_m2") is not None:
            sep_path = run.get("separation_path")
            if not sep_path or not _resolve(sep_path).exists():
                problems.append("W_sep given without separation file")
            else:
                s = json.loads(_resolve(sep_path).read_text())
                ws = (s["E_film_rigid_eV"] + s["E_substrate_rigid_eV"] - s["E_interface_eV"]) / s["area_A2"] * EV_A2_TO_J_M2
                if s.get("checkpoint_sha256") != checkpoint:
                    problems.append("separation checkpoint differs")
                if abs(s["area_A2"] - area) > 1e-6 or abs(s["E_interface_eV"] - e["interface"]) > 1e-6:
                    problems.append("separation cell/energy does not match the joined run")
                if abs(ws - run["W_sep_J_m2"]) > TOL_J_M2:
                    problems.append(f"W_sep arithmetic mismatch (recomputed {ws:.6f})")
    return problems


def analyse(index_path, table_path=SULFIDE_TABLE):
    index = load_index(index_path)
    table = json.loads(Path(table_path).read_text())
    if table.get("sha256") != SULFIDE_SHA or table.get("status") != "frozen":
        raise ValueError("Thermodynamic table is not the frozen sulfide table")
    cohort = index.get("cohort") or []
    if not cohort:
        raise ValueError("Index declares no cohort")
    runs = {r["run_id"]: dict(r) for r in index["runs"]}
    for r in runs.values():
        r["problems"] = source_problems(r, index["checkpoint_sha256"]) if r["status"] == "valid" else []
        r["validated"] = r["status"] == "valid" and not r["problems"]
    rows, compute = [], {"new": {"calls": 0, "wall_seconds": 0.0}, "reused": {"calls": 0, "wall_seconds": 0.0}}
    for r in runs.values():
        key = "reused" if r.get("reused_from") else "new"
        compute[key]["calls"] += r.get("calculator_calls") or 0
        compute[key]["wall_seconds"] += r.get("wall_seconds") or 0.0
    menu = {c["candidate_id"]: c for c in index["menu"]}
    for slot in cohort:
        cid = slot["candidate_id"]
        row = dict(candidate_id=cid, formula=menu[cid]["formula"], slot_reason=slot.get("slot_reason"),
                   thermo=thermo_card(table, cid), contacts={})
        for contact in CONTACTS:
            mine = [r for r in runs.values() if r["candidate_id"] == cid and r["contact"] == contact]
            primary = [r for r in mine if r["role"] == "primary"]
            ok = [r for r in primary if r["validated"]]
            cells = {(round(r.get("area_A2") or 0, 6), r.get("n_atoms")) for r in ok}
            selected = min(ok, key=lambda r: r["joined_energy_eV"]) if ok and len(cells) == 1 else None
            if not primary:
                status = "missing"
            elif any(r["status"] == "pending" for r in primary):
                status = "pending"
            elif selected:
                status = "validated"
            elif ok:
                status = "non-comparable cells"
            else:
                status = "failed"
            sens = [dict(run_id=r["run_id"], kind=r.get("sensitivity_kind"), status=r["status"],
                         validated=r["validated"], W_adh_J_m2=r.get("W_adh_J_m2") if r["validated"] else None,
                         delta_vs_selected=(r["W_adh_J_m2"] - selected["W_adh_J_m2"]) if r["validated"] and selected else None)
                    for r in mine if r["role"] == "sensitivity"]
            row["contacts"][contact] = dict(
                status=status, selected_run_id=selected and selected["run_id"],
                W_adh_J_m2=selected and selected["W_adh_J_m2"], W_sep_J_m2=selected and selected.get("W_sep_J_m2"),
                registry_range_J_m2=[min(r["W_adh_J_m2"] for r in ok), max(r["W_adh_J_m2"] for r in ok)] if ok else None,
                primary=[dict(run_id=r["run_id"], registry=r.get("registry"), status=r["status"], validated=r["validated"],
                              W_adh_J_m2=r.get("W_adh_J_m2") if r["validated"] else None,
                              problems=r["problems"], failure_reason=r.get("failure_reason")) for r in primary],
                sensitivity=sens, warnings=sorted({w for r in primary for w in r.get("warnings", [])}))
        w = [row["contacts"][c]["W_adh_J_m2"] for c in CONTACTS]
        row["weaker_W_adh_J_m2"] = min(w) if None not in w else None
        rows.append(row)
    return dict(index=str(index_path), checkpoint_sha256=index["checkpoint_sha256"], thermo_table_sha256=SULFIDE_SHA,
                cohort=rows, compute=compute,
                invalid_runs=[dict(run_id=r["run_id"], problems=r["problems"]) for r in runs.values() if r["problems"]],
                notes=["Registry/sensitivity spreads are finite tested ranges, not confidence intervals.",
                       "Contact models are formally polar; Li transport is not tested.",
                       "No combined score or adhesion threshold; acceptance labels are the frozen thermodynamic ones."])


def table_markdown(out):
    lines = ["| Coating | Slot | Penalty (bin) | Acceptable | Cathode W_adh (registry range) | Electrolyte W_adh (registry range) | Weaker W_adh |",
             "|---|---|---|---|---|---|---|"]
    fmt = lambda c: (f"{c['W_adh_J_m2']:.2f} ({c['registry_range_J_m2'][0]:.2f}–{c['registry_range_J_m2'][1]:.2f})"
                     if c["status"] == "validated" else c["status"])
    for r in out["cohort"]:
        t = r["thermo"]
        weaker = "—" if r["weaker_W_adh_J_m2"] is None else format(r["weaker_W_adh_J_m2"], ".2f")
        lines.append(f"| {r['formula']} | {r['slot_reason']} | {t['penalty']:.3f} ({t['penalty_bin']}) | {t['acceptable']} | "
                     f"{fmt(r['contacts']['cathode'])} | {fmt(r['contacts']['electrolyte'])} | "
                     f"{weaker} |")
    return "\n".join(lines) + "\n\nW_adh in J/m² (selected primary registry). Ranges are tested registry spreads, not confidence intervals.\n"


def plot(out, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = out["cohort"]
    labels = [f"{r['formula']}\npenalty {r['thermo']['penalty']:.3f}{' ✓' if r['thermo']['acceptable'] else ''}" for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharey=True)
    for ax, contact in zip(axes, CONTACTS):
        for i, r in enumerate(rows):
            c = r["contacts"][contact]
            if c["status"] != "validated":
                ax.text(i, 0.1, c["status"], ha="center", fontsize=9, color="#52514e")
                continue
            lo, hi = c["registry_range_J_m2"]
            ax.vlines(i, lo, hi, color="#2a78d6", lw=6, alpha=0.3)
            ax.plot(i, c["W_adh_J_m2"], "o", color="#2a78d6", ms=8, label="W_adh (selected registry)" if i == 0 else None)
            if c["W_sep_J_m2"] is not None:
                ax.plot(i, c["W_sep_J_m2"], "o", mfc="none", color="#52514e", ms=8, label="W_sep (rigid)" if i == 0 else None)
            for s in c["sensitivity"]:
                if s["W_adh_J_m2"] is not None:
                    ax.plot(i + 0.15, s["W_adh_J_m2"], "x", color="#eb6834", ms=7)
        ax.set(title=f"{contact} contact", xticks=range(len(rows)), xticklabels=labels, xlim=(-0.6, len(rows) - 0.4))
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.grid(axis="y", color="#e4e3df", lw=0.6)
    axes[0].set_ylabel("J/m²")
    axes[0].plot([], [], "x", color="#eb6834", label="sensitivity runs")
    axes[0].vlines([], 0, 0, color="#2a78d6", lw=6, alpha=0.3, label="registry range (tested, not a CI)")
    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center", ncol=4, fontsize=9, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    fig.savefig(path, dpi=200)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--index", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True, help="Output directory for summary.json, table.md, comparison.png")
    args = p.parse_args()
    out = analyse(args.index)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "summary.json").write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    (args.out / "table.md").write_text(table_markdown(out))
    plot(out, args.out / "comparison.png")
    print(table_markdown(out))
    if out["invalid_runs"]:
        print("Invalid runs (kept, not validated):", json.dumps(out["invalid_runs"], indent=1))


if __name__ == "__main__":
    main()
