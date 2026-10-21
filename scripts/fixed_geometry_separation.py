#!/usr/bin/env python3
"""Fixed-geometry work of separation for completed run_petmad_interface.py runs.

Splits the relaxed joined interface into its film and substrate atoms without re-relaxing
(same cell, positions, PBC) and evaluates two single points:
  W_sep,fixed = (E_film^rigid + E_sub^rigid - E_interface) / A.
The gap to the independently relaxed W_adh is exactly the separated slabs' relaxation
energy per area, i.e. how much each free surface rearranges once the contact is removed.
"""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from ase.io import read
from interphaise.tools.energetics import EV_PER_A2_TO_J_PER_M2


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('runs',type=Path,nargs='+');ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--threads',type=int,default=4)
    args=ap.parse_args()
    import torch;torch.set_num_threads(args.threads)
    from upet.ase import UPETCalculator
    sha=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest()
    calc=UPETCalculator(checkpoint_path=str(args.checkpoint),device='cpu')
    for run in args.runs:
        r=json.loads((run/'result.json').read_text());R=r['relaxations']
        labels=read(run/'initial.extxyz').arrays['interface_label']
        joined=read(run/'interface/final.extxyz')
        out={'checkpoint_sha256':sha,'area_A2':r['area_A2'],'E_interface_eV':R['interface']['final_energy_eV']}
        for part in ('film','substrate'):
            atoms=joined[np.where(labels==part)[0]];atoms.calc=calc
            out[f'E_{part}_rigid_eV']=float(atoms.get_potential_energy())
            out[f'E_{part}_relaxed_eV']=R[part]['final_energy_eV']
            out[f'{part}_relaxation_J_m2']=(out[f'E_{part}_rigid_eV']-out[f'E_{part}_relaxed_eV'])/r['area_A2']*EV_PER_A2_TO_J_PER_M2
        out['W_sep_fixed_geometry_J_m2']=(out['E_film_rigid_eV']+out['E_substrate_rigid_eV']-out['E_interface_eV'])/r['area_A2']*EV_PER_A2_TO_J_PER_M2
        out['W_adh_relaxed_J_m2']=r['work_of_adhesion_J_m2']
        (run/'fixed_geometry_separation.json').write_text(json.dumps(out,indent=2)+'\n')
        print(f"{run.name}: W_sep(fixed) {out['W_sep_fixed_geometry_J_m2']:.4f}  W_adh(relaxed) {out['W_adh_relaxed_J_m2']:.4f}  "
              f"relaxation: film {out['film_relaxation_J_m2']:.4f} substrate {out['substrate_relaxation_J_m2']:.4f} J/m²",flush=True)

if __name__=='__main__':main()
