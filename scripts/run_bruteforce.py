"""Brute-force baseline: no LLM, every low-index facet pair, every termination.

This is the InterOptimus-style exhaustive search the agent is compared
against. It reports how many single points / relaxations it needed and the
best W_adh it found, so the headline comparison is

    agent: same (or better) best interface with N_agent ≪ N_brute relaxations

    python scripts/run_bruteforce.py --case 0 [--max-index 1] [--dry-run]
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import config  # noqa: E402
from interphaise.log import RunLog, _default  # noqa: E402
from interphaise.tools import energetics  # noqa: E402
from interphaise.tools.materials import get_bulk  # noqa: E402
from interphaise.tools.matcher import MatchSettings, enumerate_interfaces, low_index_millers  # noqa: E402
from interphaise.tools.mlip import load_mlip  # noqa: E402
from interphaise.tools.validation import oxidation_map, validate  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", type=int, default=0)
    ap.add_argument("--max-index", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--top-per-pair", type=int, default=2, help="relax the N best-registry candidates per facet pair")
    args = ap.parse_args()

    ctx = config.CASES[args.case]
    sub, film = get_bulk(ctx.electrode), get_bulk(ctx.electrolyte)
    s_oxi, f_oxi = oxidation_map(sub), oxidation_map(film)
    log = RunLog(ctx.name + "_bruteforce")
    calc = None if args.dry_run else load_mlip(config.MLIP_CATHODE if ctx.role == "cathode" else config.MLIP_ANODE)

    rows = []
    for sm, fm in itertools.product(low_index_millers(sub, args.max_index), low_index_millers(film, args.max_index)):
        found = enumerate_interfaces(sub, film, sm, fm, (ctx.electrode, ctx.electrolyte), MatchSettings())
        valid = [(c, i) for c, i in found
                 if validate(c, i, max_atoms=ctx.max_atoms, max_strain=ctx.max_strain, film_oxi=f_oxi,
                             substrate_oxi=s_oxi, film_formula=ctx.electrolyte, substrate_formula=ctx.electrode)[0]]
        valid.sort(key=lambda t: t[0].n_atoms)
        for cand, iface in valid[: args.top_per_pair]:
            row = {"candidate": cand}
            if calc is not None:
                res, _, _ = energetics.work_of_adhesion(cand, iface, calc)
                row["w_adh"] = res.w_adh
            rows.append(row)
        log.record("bruteforce", "compute", {"facets": (sm, fm), "n_found": len(found), "n_valid": len(valid)})

    best = max((r for r in rows if "w_adh" in r), key=lambda r: r["w_adh"], default=None)
    summary = {"case": ctx.name, "n_candidates_computed": len(rows), "best": best,
               "counters": {"single_points": energetics.Counter.single_points,
                            "relaxations": energetics.Counter.relaxations}}
    log.record("summary", "compute", summary)
    print(json.dumps(summary, indent=1, default=_default))


if __name__ == "__main__":
    main()
