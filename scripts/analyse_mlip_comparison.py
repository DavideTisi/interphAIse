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
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from interphaise.pilot import CONTACTS, comparable_problems, contact_summary, evaluate_runs, load_index, thermo_card

SULFIDE_TABLE = ROOT / "data/benchmarks/environment_v1/lco_lpscl_4v.json"
SULFIDE_SHA = "f70342c9aae0bd0e95f588bfb8c2f956815b3cf336c24e866119f7ab7f45f510"


def analyse(index_path, table_path=SULFIDE_TABLE):
    index = load_index(index_path)
    table = json.loads(Path(table_path).read_text())
    if table.get("sha256") != SULFIDE_SHA or table.get("status") != "frozen":
        raise ValueError("Thermodynamic table is not the frozen sulfide table")
    cohort = index.get("cohort") or []
    if not cohort:
        raise ValueError("Index declares no cohort")
    runs = {k: r for k, r in evaluate_runs(index, ROOT).items() if r["role"] != "consistency"}
    for r in runs.values():
        r["validated"] = r["evidence"] == "valid"
    rows, compute = [], {k: {"calls": 0, "wall_seconds": 0.0, "runs_with_unknown_cost": 0} for k in ("new", "reused")}
    for r in runs.values():
        bucket = compute["reused" if r.get("reused_from") else "new"]
        if r.get("calculator_calls") is None:
            bucket["runs_with_unknown_cost"] += r["status"] not in ("pending",) and r["evidence"] != "unavailable"
        else:
            bucket["calls"] += r["calculator_calls"]
            bucket["wall_seconds"] += r.get("wall_seconds") or 0.0
    menu = {c["candidate_id"]: c for c in index["menu"]}
    for slot in cohort:
        cid = slot["candidate_id"]
        row = dict(candidate_id=cid, formula=menu[cid]["formula"], slot_reason=slot.get("slot_reason"),
                   thermo=thermo_card(table, cid), contacts={})
        for contact in CONTACTS:
            mine = [r for r in runs.values() if r["candidate_id"] == cid and r["contact"] == contact]
            primary = [r for r in mine if r["role"] == "primary"]
            ok = [r for r in primary if r["validated"]]
            noncomparable = comparable_problems(primary) if primary else []
            if not primary:
                status = "missing"
            elif any(r["evidence"] == "invalid_evidence" for r in primary):
                status = "invalid evidence"
            elif any(r["evidence"] == "pending" for r in primary):
                status = "pending"
            elif noncomparable:
                status = "non-comparable registries"
            else:
                status = "validated" if ok else "failed"
            summary = contact_summary(mine, contact) if status == "validated" else {}
            sens = [dict(run_id=r["run_id"], kind=r.get("sensitivity_kind"), status=r["evidence"],
                         reason=r.get("failure_reason") if r["evidence"] == "unavailable" else None,
                         W_adh_J_m2=r["W_adh_J_m2"] if r["validated"] else None,
                         delta_vs_selected=(r["W_adh_J_m2"] - summary["W_adh_J_m2"]) if r["validated"] and summary else None)
                    for r in mine if r["role"] == "sensitivity"]
            row["contacts"][contact] = dict(
                status=status, selected_run_id=summary.get("selected_run_id"), W_adh_J_m2=summary.get("W_adh_J_m2"),
                W_sep_J_m2=summary.get("W_sep_J_m2"), registry_range_J_m2=summary.get("registry_range_J_m2"),
                comparability_problems=noncomparable,
                primary=[dict(run_id=r["run_id"], registry_id=r.get("registry_id"), status=r["evidence"],
                              W_adh_J_m2=r["W_adh_J_m2"] if r["validated"] else None, problems=r["problems"],
                              failure_reason=r.get("failure_reason")) for r in primary],
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
