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


def test_cell_relaxation_records_lattice_stress_and_symmetry(tmp_path):
    from ase.build import bulk
    from ase.calculators.emt import EMT
    from interphaise.tools.relaxation import relax_cell_record
    reference=bulk('Cu','fcc',a=3.6,cubic=True)
    reference.calc=EMT()
    _,ref=relax_cell_record(reference,CountedCalculator(EMT()),tmp_path/'ref',fmax=.001,smax_GPa=.01)
    strained=reference.copy();strained.set_cell(strained.cell*1.03,scale_atoms=True)
    final,r=relax_cell_record(strained,CountedCalculator(EMT()),tmp_path/'run',fmax=.001,smax_GPa=.01)
    assert r['converged'] and r['final']['max_abs_stress_GPa']<=.01
    assert abs(r['initial']['stress_GPa'][0])>1
    assert np.isclose(final.cell.cellpar()[0],ref['final']['cellpar'][0],atol=1e-3)
    assert r['initial']['space_group'][1e-3]==r['final']['space_group'][1e-3]=='Fm-3m (225)'
    assert (tmp_path/'run'/'final.extxyz').exists() and r['calculator_calls']>0


def test_cell_relaxation_exhaustion_and_stress_gate_are_explicit(tmp_path):
    from ase.build import bulk
    from ase.calculators.emt import EMT
    from interphaise.tools.relaxation import relax_cell_record
    strained=bulk('Cu','fcc',a=3.75,cubic=True)
    _,r=relax_cell_record(strained,CountedCalculator(EMT()),tmp_path,steps=0)
    # Forces vanish by symmetry, so only the stress criterion keeps this unconverged.
    assert not r['converged'] and r['steps']==0
    assert r['final']['max_force_eV_A']<1e-8 and r['final']['max_abs_stress_GPa']>.05


def test_explicit_termination_is_enumerated_before_the_cap(monkeypatch):
    import pytest
    from interphaise.tools import matcher
    from pymatgen.core import Lattice,Structure
    def iface(n):
        s=Structure(Lattice.cubic(5+n),['H'],[[0,0,0]])
        s.interface_properties={'von_mises_strain':.01};return s
    class TwoTerminations:
        zsl_matches=[object()]
        terminations=[('A','x'),('F','y')]
        def __init__(self,**kwargs):pass
        def get_interfaces(self,term,**kwargs):
            return [iface(i) for i in range(3)]
    monkeypatch.setattr(matcher,'CoherentInterfaceBuilder',TwoTerminations)
    capped=matcher.MatchSettings(max_candidates=3)
    report={}
    out=matcher.enumerate_interfaces(None,None,(0,0,1),(0,0,1),('s','f'),capped,report=report)
    assert {c.termination for c,_ in out}=={('A','x')} and report['truncated']
    report={}
    out=matcher.enumerate_interfaces(None,None,(0,0,1),(0,0,1),('s','f'),capped,terminations=[('F','y')],report=report)
    assert {c.termination for c,_ in out}=={('F','y')} and len(out)==3
    with pytest.raises(ValueError):
        matcher.enumerate_interfaces(None,None,(0,0,1),(0,0,1),('s','f'),capped,terminations=[('Q','z')])


def test_fixed_depth_does_not_grow_with_slab_thickness():
    from interphaise.tools.energetics import bottom_fixed_indices
    def slab(layers):
        return Atoms('H'*layers,positions=[[0,0,1.5*k] for k in range(layers)],cell=[5,5,40])
    thin,thick=slab(4),slab(8)
    assert bottom_fixed_indices(thin,range(4),depth=1.6)==bottom_fixed_indices(thick,range(8),depth=1.6)==[0,1]
    assert len(bottom_fixed_indices(thick,range(8),.34))>len(bottom_fixed_indices(thin,range(4),.34))
