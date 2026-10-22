"""F1: an exhausted relaxation must never become a validated work of adhesion."""
import json

from ase import Atoms
from ase.calculators.calculator import Calculator, all_changes

from interphaise.llm import ScriptedLLM
from interphaise.orchestrator import Orchestrator
from interphaise.tools import energetics
from interphaise.tools.mlip import load_mlip
from tests.test_orchestrator import INTERPHASE, ctx, facets, settings


class Harmonic(Calculator):
    implemented_properties = ['energy', 'forces']

    def calculate(self, atoms=None, properties=('energy',), system_changes=all_changes):
        super().calculate(atoms, properties, system_changes)
        self.results = {'energy': float((atoms.positions**2).sum() / 2), 'forces': -atoms.positions.copy()}


def test_relax_reports_exhausted_budget():
    atoms = Atoms('H', positions=[[1, 0, 0]], cell=[10, 10, 10])
    _, energy, converged = energetics.relax(atoms, Harmonic(), fmax=0.01, steps=0)
    assert energy == 0.5 and converged is False
    _, _, converged = energetics.relax(atoms, Harmonic(), fmax=0.01, steps=500)
    assert converged is True


def test_unconverged_relaxations_give_no_adhesion_and_are_never_judged(tmp_path, toy_bulk, toy_entries):
    judged = []

    def judge(system, user):
        judged.append(user)
        return {"verdict": "accept", "action": "none", "rationale": "should not be reached"}

    llm = ScriptedLLM({"interphase_reasoner": INTERPHASE, "facet_reasoner": facets, "physicality_judge": judge})
    out = Orchestrator(ctx(), llm, calc=load_mlip("lj"), settings=settings(steps=1), bulk_fn=toy_bulk,
                       entries_fn=toy_entries, run_root=tmp_path).run()
    assert all(p["status"] == "failed" for p in out["pairs"]) and not judged
    log = json.loads(next(tmp_path.glob("*/decision_log.json")).read_text())
    results = [e["output"]["result"] for e in log["events"] if e["stage"] == "energetics"]
    assert results and all(r["w_adh"] is None and r["status"] == "unconverged" and r["unconverged"] for r in results)
    assert all(r["w_adh_unvalidated"] is not None for r in results)   # raw value kept for diagnosis only
