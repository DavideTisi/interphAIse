#!/usr/bin/env python3
"""Independent LP/Qhull comparison on two real candidates, both contacts."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pymatgen.analysis.phase_diagram import GrandPotentialPhaseDiagram
from pymatgen.core import Element, Structure
from interphaise.discovery_evaluator import _project, _lp_contact, _contact
from interphaise.tools.thermo_dataset import load_entries, resolve_entry


def main():
    dataset,entries=load_entries(ROOT/'data/thermo/mp_gga_v2.json.gz')
    pool=json.loads((ROOT/'data/pools/mp_candidates_v2.json').read_text())
    mu=min(e.energy_per_atom for e in entries if set(e.composition.elements)=={Element('Li')})-4
    checks=[]
    for formula in ('LiF','LiNbF6'):
        candidate=next(c for c in pool['candidates'] if c['formula']==formula)
        coating=resolve_entry(entries,candidate['material_id'],Structure.from_dict(candidate['structure']))
        for role in ('electrode','electrolyte'):
            endpoint=resolve_entry(entries,dataset['endpoints'][role]['material_id'])
            allowed=set(coating.composition.elements)|set(endpoint.composition.elements)|{Element('Li')}
            subset=[e for e in entries if set(e.composition.elements)<=allowed]
            gpd=GrandPotentialPhaseDiagram(subset,{Element('Li'):mu})
            first,second=_project(endpoint,mu),_project(coating,mu)
            for mode in ('pinned','equilibrated'):
                refs=None if mode=='pinned' else (
                    gpd.get_hull_energy_per_atom(first.composition),gpd.get_hull_energy_per_atom(second.composition))
                lp=_lp_contact(subset,mu,first,second,refs)
                hull=_contact(gpd,first,second,refs)
                difference=abs(lp['reaction_energy']-hull['reaction_energy'])
                check={'formula':formula,'endpoint':role,'reference':mode,'entries':len(subset),
                       'lp_energy':lp['reaction_energy'],'qhull_energy':hull['reaction_energy'],
                       'absolute_difference_eV_non_Li_atom':difference}
                checks.append(check);print(json.dumps(check),flush=True)
                if difference>1e-7:raise ValueError('Solver discrepancy')
    output={'dataset_sha256':dataset['sha256'],'tolerance_eV_non_Li_atom':1e-7,'checks':checks}
    (ROOT/'runs/solver_crosscheck.json').write_text(json.dumps(output,indent=2)+'\n')

if __name__=='__main__':main()
