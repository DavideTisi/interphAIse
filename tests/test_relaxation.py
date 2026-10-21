import numpy as np
from ase import Atoms
from ase.calculators.calculator import Calculator,all_changes
from interphaise.tools.relaxation import CountedCalculator,relax_record


class Harmonic(Calculator):
    implemented_properties=['energy','forces']
    def calculate(self,atoms=None,properties=('energy',),system_changes=all_changes):
        super().calculate(atoms,properties,system_changes)
        self.results={'energy':float((atoms.positions**2).sum()/2),'forces':-atoms.positions.copy()}


def test_counting_excludes_cached_properties():
    atoms=Atoms('H',positions=[[1,0,0]],cell=[10,10,10])
    calc=CountedCalculator(Harmonic());atoms.calc=calc
    atoms.get_potential_energy();atoms.get_forces()
    assert calc.calls==1
    atoms.positions[0,0]=2
    atoms.get_forces()
    assert calc.calls==2


def test_exhausted_relaxation_is_explicit(tmp_path):
    atoms=Atoms('H',positions=[[1,0,0]],cell=[10,10,10])
    _,r=relax_record(atoms,CountedCalculator(Harmonic()),tmp_path,steps=0,fmax=.01)
    assert not r['converged'] and r['steps']==0
    assert r['max_free_force_eV_A']==1


def test_convergence_uses_free_forces_and_reports_fixed_reaction_force(tmp_path):
    atoms=Atoms('HH',positions=[[1,0,0],[2,0,0]],cell=[10,10,10])
    final,r=relax_record(atoms,CountedCalculator(Harmonic()),tmp_path,fixed=[0],steps=200,fmax=.02)
    assert r['converged'] and r['max_free_force_eV_A']<=.02
    assert r['max_unconstrained_force_eV_A']>=1
    assert np.allclose(final.positions[0],atoms.positions[0])


def test_no_lattice_match_returns_empty(monkeypatch):
    from interphaise.tools import matcher
    class NoMatch:
        zsl_matches=[]
        def __init__(self,**kwargs):pass
    monkeypatch.setattr(matcher,'CoherentInterfaceBuilder',NoMatch)
    assert matcher.enumerate_interfaces(None,None,(0,0,1),(0,0,1),('a','b'))==[]
