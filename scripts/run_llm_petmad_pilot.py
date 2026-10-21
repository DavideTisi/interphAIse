"""Advance the LLM-guided PET-MAD pilot one stage at a time (LLM_PETMAD_PILOT_PLAN.md).

    python scripts/run_llm_petmad_pilot.py --state STATE.json --index INDEX.json --mock     # offline
    python scripts/run_llm_petmad_pilot.py --state STATE.json --index INDEX.json --live     # paid, capped

Runs stages until the next one needs physics that is not yet terminal (exit 2, resume later), the
pilot completes, or the HTTP cap would be exceeded. --live requires Davide's cost approval and uses
only direct Anthropic claude-haiku-5-5, temperature 1.0, max 4096 output tokens.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from interphaise.pilot import Pending, Pilot


class MockLLM:
    """Deterministic stand-in: ranks the unevaluated IDs as given and predicts fixed ranges."""
    def __init__(self):
        self.last_metadata = None

    def __call__(self, system, user):
        data = json.loads(user)
        self.last_metadata = {"http_attempts": 1, "returned_model": "mock", "usage": None}
        if data["stage"] == "summary":
            return {"summary": "mock summary"}
        out = {"ordered_shortlist": data["unevaluated"], "hypothesis": "mock hypothesis"}
        if data["stage"] != "prior":
            out.update(selected_id=data["unevaluated"][0], predicted_weaker_contact="electrolyte",
                       predicted_W_adh_J_m2={"cathode": [2.0, 4.0], "electrolyte": [1.0, 2.0]},
                       change_trigger="mock trigger", supporting_observations=["mock observation"])
        return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--index", type=Path, default=ROOT / "data/petmad/coating_comparison_v1/index.json")
    p.add_argument("--table", type=Path, default=ROOT / "data/benchmarks/environment_v1/lco_lpscl_4v.json")
    p.add_argument("--reference", default="mp-aaacjjwh")
    p.add_argument("--no-prior", action="store_true", help="Skip the optional chemistry-only prior snapshot")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--mock", action="store_true")
    mode.add_argument("--live", action="store_true")
    args = p.parse_args()
    if args.live:
        from interphaise.llm import make_llm
        llm = make_llm("anthropic/claude-haiku-5-5", temperature=1.0, max_tokens=4096)
    else:
        llm = MockLLM()
    pilot = Pilot(args.state, args.index, args.table, reference_id=args.reference, include_prior=not args.no_prior)
    try:
        while (record := pilot.run_stage(llm)) is not None:
            print(f"{record['stage']}: {record['parsed'].get('selected_id', '')} (HTTP used {pilot.state['http_attempts_used']})")
    except Pending as exc:
        print(f"pending: {exc}; resume when the feedback is terminal")
        sys.exit(2)
    print(f"status: {pilot.state['status']}")
    print(json.dumps(pilot.assessment(), indent=2))


if __name__ == "__main__":
    main()
