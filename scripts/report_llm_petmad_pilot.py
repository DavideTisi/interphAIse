"""Decision timeline, prediction checks and figure for the LLM-guided PET-MAD pilot (read-only).

    python scripts/report_llm_petmad_pilot.py --state data/experiments/llm_petmad_pilot_v1/state.json \
        --out data/experiments/llm_petmad_pilot_v1/report

Reads a saved pilot state (no lock, no index): every attempt in order, the frozen feedback each decision
saw, the model's forecasts against the observed primary-registry W_adh, and the decision comparison.
Forecast ranges are the model's stated ranges, not calibrated intervals; three coating slots are a
demonstration of the feedback loop, not evidence of better search. A mock state is labelled MOCK.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from interphaise.pilot import CONTACTS, assess

LIMITS = ["Forecast ranges are model statements, not calibrated confidence intervals.",
          "Two new coatings cannot establish search superiority or statistical significance.",
          "The unchosen coating in the decision comparison has no measured outcome.",
          "Contact models are formally polar; Li transport is not tested; sensitivity checks are reported separately."]


def _fmt(x, nd=3):
    return "—" if x is None else f"{x:.{nd}f}"


def _cut(text, n=160):
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[: n - 1] + "…"


def report(state):
    mock = state["mode"] != "live"
    formulas = {}
    for r in state["stages"]:
        if r.get("prompt"):
            formulas.update({c["candidate_id"]: c["formula"] for c in json.loads(r["prompt"]).get("candidates", [])})
    name = lambda cid: formulas.get(cid, cid)
    lines = [f"# LLM-guided PET-MAD pilot{' — MOCK (no live model)' if mock else ''}", "",
             f"Status: **{state['status']}**. Mode `{state['mode']}`, settings `{json.dumps(state['settings'])}`. "
             f"HTTP attempts used {state['http_attempts_used']} of {state['http_cap']} (reservations unsettled: "
             f"{state.get('http_reserved_unsettled', 0)}). Menu `{state['menu_sha256'][:12]}`, table `{state['table_sha256'][:12]}`, "
             f"manifest `{(state.get('manifest_sha256') or '—')[:12]}`.", "",
             "## Decision timeline", "",
             "| # | Stage | Attempt | Selected | Shortlist | Hypothesis | Forecast W_adh cathode / electrolyte (J/m²) | Weaker (pred.) | Change trigger | Prior-prediction assessment | Feedback seen | HTTP | Record |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(state["stages"], start=1):
        if r.get("failed"):
            lines.append(f"| {i} | {r['stage']} | — | stopped: {r.get('reason', '')} | | | | | | | | | |")
            continue
        p = r.get("parsed") or {}
        rng = p.get("predicted_W_adh_J_m2") or {}
        fc = " / ".join(f"[{v[0]:g}, {v[1]:g}]" for v in (rng.get("cathode"), rng.get("electrolyte")) if v) or "—"
        sel = name(p["selected_id"]) if p.get("selected_id") else ("error: " + _cut(r.get("error", ""), 80) if r.get("error") else "—")
        lines.append(f"| {i} | {r['stage']} | {r['attempt']} | {sel} | {', '.join(name(c) for c in p.get('ordered_shortlist', []))} | "
                     f"{_cut(p.get('hypothesis', ''))} | {fc} | {p.get('predicted_weaker_contact', '—')} | {_cut(p.get('change_trigger', ''), 100)} | "
                     f"{_cut(p.get('prior_prediction_assessment', ''), 120)} | {', '.join(h[:8] for h in r.get('feedback_sha256', [])) or '—'} | "
                     f"{r.get('http_attempts_charged', '—')} | {r.get('record_sha256', '')[:12]} |")
    a = assess(state)
    lines += ["", "## Prediction checks (observed = selected primary registry)", "",
              "| Decision | Coating | Contact | Forecast | Width | Observed | In range | Miss | Weaker pred./obs. | Agrees |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for row in a["predictions"]:
        if row["status"] != "revealed":
            lines.append(f"| {row['stage']} | {name(row['candidate_id'])} | — | — | — | {row['status']} | | | | |")
            continue
        for c in CONTACTS:
            k = row["contacts"][c]
            lines.append(f"| {row['stage']} | {row['formula']} | {c} | [{k['predicted'][0]:g}, {k['predicted'][1]:g}] | {k['width']:g} | "
                         f"{_fmt(k['observed'])} | {'—' if k['in_range'] is None else k['in_range']} | {_fmt(k['miss'])} | "
                         f"{row['weaker_predicted']} / {row['weaker_observed']} | {'—' if row['weaker_agrees'] is None else row['weaker_agrees']} |")
    comp = a["decision_comparison"]
    lines += ["", "## Decision comparison", "",
              ("Not available until both choices are made." if comp is None else
               f"Next in the choose-2 shortlist: {name(comp['initial_next'])}; chosen at choose-3: {name(comp['chosen'])}; "
               f"changed: **{comp['changed']}**. {comp['note']}"),
              "", "## Limitations", "", *[f"- {x}" for x in LIMITS]]
    return "\n".join(lines) + "\n", a


def plot(state, a, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rows = [r for r in a["predictions"] if r["status"] == "revealed"]
    if not rows:
        return False
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, c in zip(axes, CONTACTS):
        for i, r in enumerate(rows):
            k = r["contacts"][c]
            ax.vlines(i, *k["predicted"], color="#2a78d6", lw=8, alpha=0.35, label="model forecast" if i == 0 else None)
            if k["observed"] is not None:
                ax.plot(i, k["observed"], "o", color="#0b0b0b", ms=8, label="observed W_adh" if i == 0 else None)
            else:
                ax.text(i, k["predicted"][0], "no valid result", ha="center", va="top", fontsize=8, color="#52514e")
        ax.set(title=f"{c} contact", xticks=range(len(rows)), xticklabels=[f"{r['formula']}\n({r['stage']})" for r in rows],
               xlim=(-0.6, len(rows) - 0.4))
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.grid(axis="y", color="#e4e3df", lw=0.6)
    axes[0].set_ylabel("W_adh (J/m²)")
    fig.legend(*axes[0].get_legend_handles_labels(), loc="upper center", ncol=2, frameon=False, fontsize=9)
    fig.text(0.5, 0.01, ("MOCK — " if state["mode"] != "live" else "") + "Forecasts are model statements, not calibrated intervals",
             ha="center", va="bottom", fontsize=9, color="#52514e")
    fig.tight_layout(rect=(0, 0.06, 1, 0.93))
    fig.savefig(path, dpi=200)
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    state = json.loads(args.state.read_text())
    text, a = report(state)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "report.md").write_text(text)
    (args.out / "assessment.json").write_text(json.dumps(a, indent=2, allow_nan=False) + "\n")
    drew = plot(state, a, args.out / "predictions.png")
    print(text)
    print(f"Saved {args.out}" + ("" if drew else " (no revealed choices yet, figure skipped)"))


if __name__ == "__main__":
    main()
