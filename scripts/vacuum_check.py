#!/usr/bin/env python3
"""Vacuum (periodic-image isolation) check on completed run_petmad_interface.py runs.

For each requested vacuum the normal cell length is increased by (vacuum - base) without
scaling coordinates, and single points are evaluated for the saved relaxed interface, both
relaxed separated references and both rigid fragments of the relaxed interface. Same masks
as the relaxation. Reports W_adh, W_sep, free-atom forces against the relaxation target and
the actual empty separation along z (largest periodic gap between atomic planes).
A finite-range model cannot couple images across a gap wider than its neighbour cutoff,
so this checks isolation numerically; it says nothing about real polar electrostatics.
"""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from ase.constraints import FixAtoms
from interphaise.tools.energetics import EV_PER_A2_TO_J_PER_M2
from interphaise.tools.provenance import checkpoint_sha256,load_valid_interface_run,ProvenanceError


def empty_gap(atoms):
    z=np.sort(atoms.get_scaled_positions(wrap=True)[:,2])*atoms.cell[2,2]
    return float(max(np.max(np.diff(z)) if len(z)>1 else 0,z[0]+atoms.cell[2,2]-z[-1]))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('runs',type=Path,nargs='+');ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--vacuum',type=float,nargs='+',default=[15,20,25]);ap.add_argument('--base',type=float,default=15)
    ap.add_argument('--threads',type=int,default=8)
    args=ap.parse_args()
    sha=checkpoint_sha256(args.checkpoint)
    # F2: validate every source run before loading the model; a mismatch writes nothing.
    try:runs={run:load_valid_interface_run(run,sha) for run in args.runs}
    except ProvenanceError as error:ap.error(str(error))
    import torch;torch.set_num_threads(args.threads)
    from upet.ase import UPETCalculator
    calc=UPETCalculator(checkpoint_path=str(args.checkpoint),device='cpu')
    for run,valid in runs.items():
        r=valid['result'];records=valid['records'];labels=valid['labels'];saved=valid['finals']
        rigid={k:saved['interface'][np.where(labels==k)[0]] for k in ('film','substrate')}
        masks={k:records[k]['fixed_atom_indices'] for k in ('interface','film','substrate')}
        out={'run':str(run),'checkpoint_sha256':sha,'area_A2':r['area_A2'],'base_vacuum_A':args.base,'fmax_target_eV_A':records['interface']['fmax_target_eV_A'],'settings':{}}
        for vac in args.vacuum:
            row={'energies_eV':{},'max_free_force_eV_A':{},'empty_gap_A':{}}
            def evaluate(name,atoms,fixed):
                a=atoms.copy();cell=a.cell.array.copy();cell[2]=cell[2]/np.linalg.norm(cell[2])*(np.linalg.norm(cell[2])+vac-args.base)
                a.set_cell(cell,scale_atoms=False);a.set_constraint(FixAtoms(indices=fixed) if fixed else [])
                a.calc=calc
                row['energies_eV'][name]=float(a.get_potential_energy())
                row['max_free_force_eV_A'][name]=float(np.linalg.norm(a.get_forces(),axis=1).max())
                row['empty_gap_A'][name]=empty_gap(a)
                return a
            for k,atoms in saved.items():evaluate(k,atoms,masks[k])
            for k,atoms in rigid.items():evaluate(f'{k}_rigid',atoms,masks['substrate'] if k=='substrate' else [])
            e=row['energies_eV'];f=EV_PER_A2_TO_J_PER_M2/r['area_A2']
            row['W_adh_J_m2']=(e['film']+e['substrate']-e['interface'])*f
            row['W_sep_J_m2']=(e['film_rigid']+e['substrate_rigid']-e['interface'])*f
            out['settings'][str(vac)]=row
            print(f"{run.name} vacuum {vac:g} Å: W_adh {row['W_adh_J_m2']:.6f}  W_sep {row['W_sep_J_m2']:.6f} J/m²  "
                  f"min empty gap {min(row['empty_gap_A'].values()):.2f} Å  max free force {max(row['max_free_force_eV_A'].values()):.4f} eV/Å",flush=True)
        base=out['settings'][str(float(args.base))] if str(float(args.base)) in out['settings'] else out['settings'][str(args.base)]
        out['stored_vs_recomputed_base_eV']={k:base['energies_eV'][k]-records[k]['final_energy_eV'] for k in ('interface','film','substrate')}
        (run/'vacuum_check.json').write_text(json.dumps(out,indent=2)+'\n')
        print(f"  stored vs recomputed at base: {({k:round(v,6) for k,v in out['stored_vs_recomputed_base_eV'].items()})}",flush=True)

if __name__=='__main__':main()
