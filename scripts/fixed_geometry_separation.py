#!/usr/bin/env python3
"""Fixed-geometry work of separation for completed run_petmad_interface.py runs.

Splits the relaxed joined interface into its film and substrate atoms without re-relaxing
(same cell, positions, PBC) and evaluates two single points:
  W_sep,fixed = (E_film^rigid + E_sub^rigid - E_interface) / A.
The gap to the independently relaxed W_adh is exactly the separated slabs' relaxation
energy per area, i.e. how much each free surface rearranges once the contact is removed.
"""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from interphaise.tools.energetics import EV_PER_A2_TO_J_PER_M2
from interphaise.tools.provenance import checkpoint_sha256,load_valid_interface_run,ProvenanceError


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('runs',type=Path,nargs='+');ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--threads',type=int,default=4)
    ap.add_argument('--device',default='cpu',help="Use the joined run's device, e.g. 'cpu' or 'cuda'")
    args=ap.parse_args()
    sha=checkpoint_sha256(args.checkpoint)
    # F2: validate every source run (checkpoint, convergence, labels, cell/area) before loading the model.
    try:runs={run:load_valid_interface_run(run,sha) for run in args.runs}
    except ProvenanceError as error:ap.error(str(error))
    import torch;torch.set_num_threads(args.threads)
    from upet.ase import UPETCalculator
    calc=UPETCalculator(checkpoint_path=str(args.checkpoint),device=args.device)
    for run,valid in runs.items():
        r=valid['result'];R=r['relaxations'];labels=valid['labels'];joined=valid['finals']['interface']
        out={'checkpoint_sha256':sha,'source_checkpoint_sha256':r['checkpoint_sha256'],
             'device':args.device,'joined_run_device':r.get('device','cpu'),
             'area_A2':r['area_A2'],'E_interface_eV':R['interface']['final_energy_eV']}
        for part in ('film','substrate'):
            atoms=joined[np.where(labels==part)[0]];atoms.calc=calc
            out[f'E_{part}_rigid_eV']=float(atoms.get_potential_energy())
            out[f'E_{part}_relaxed_eV']=R[part]['final_energy_eV']
            out[f'{part}_relaxation_J_m2']=(out[f'E_{part}_rigid_eV']-out[f'E_{part}_relaxed_eV'])/r['area_A2']*EV_PER_A2_TO_J_PER_M2
        out['W_sep_fixed_geometry_J_m2']=(out['E_film_rigid_eV']+out['E_substrate_rigid_eV']-out['E_interface_eV'])/r['area_A2']*EV_PER_A2_TO_J_PER_M2
        out['W_adh_relaxed_J_m2']=r['work_of_adhesion_J_m2']
        if not all(np.isfinite(out[k]) for k in ('E_film_rigid_eV','E_substrate_rigid_eV','W_sep_fixed_geometry_J_m2')):
            raise ProvenanceError(f'{run}: non-finite rigid-fragment energy; nothing written')
        (run/'fixed_geometry_separation.json').write_text(json.dumps(out,indent=2)+'\n')
        print(f"{run.name}: W_sep(fixed) {out['W_sep_fixed_geometry_J_m2']:.4f}  W_adh(relaxed) {out['W_adh_relaxed_J_m2']:.4f}  "
              f"relaxation: film {out['film_relaxation_J_m2']:.4f} substrate {out['substrate_relaxation_J_m2']:.4f} J/m²",flush=True)

if __name__=='__main__':main()
