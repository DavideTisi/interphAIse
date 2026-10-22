#!/usr/bin/env python3
"""PET-MAD bulk relaxation (positions + lattice) of the pinned structures used to build interfaces.

Each conventional standard cell is relaxed with its space group kept (FixSymmetry) and a
FrechetCellFilter. A stability check then rattles the result and relaxes it again without
symmetry: an energy drop there means the model prefers a distorted structure.
Converged means max force <= --fmax AND max |stress| <= --smax on the final structure.
"""
import argparse
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from pymatgen.io.ase import AseAtomsAdaptor
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from interphaise.tools.mlip import load_mlip
from interphaise.tools.relaxation import CountedCalculator,relax_cell_record
from interphaise.tools.thermo_dataset import load_entries,resolve_entry

COATINGS={'LiNbF6':'mp-aaacjjwh','LiCaAlF6':'mp-aaaaajby','LiZr2(PO4)3':'mp-aaabevhd'}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output',type=Path,default=ROOT/'runs/bulk_relaxation')
    ap.add_argument('--checkpoint',type=Path,help='Optional cached pet-mad-s-v1.6.0.ckpt for fully offline loading')
    ap.add_argument('--only',nargs='+',help='Formulas to relax (default: all five)')
    ap.add_argument('--dataset',type=Path,default=ROOT/'data/thermo/mp_gga_v2.json.gz',help='Pinned thermodynamic dataset')
    ap.add_argument('--extra',nargs='+',default=[],metavar='FORMULA=ID',help='Additional pinned entries, e.g. LiF=mp-aaaaabru')
    ap.add_argument('--fmax',type=float,default=.01)
    ap.add_argument('--smax',type=float,default=.05,help='Stress target, GPa')
    ap.add_argument('--steps',type=int,default=1000)
    ap.add_argument('--rattle',type=float,default=.02,help='Stability-check displacement, Å')
    ap.add_argument('--threads',type=int,default=2)
    args=ap.parse_args()
    if args.output.exists():ap.error('Use a fresh output directory')
    args.output.mkdir(parents=True)
    import torch
    torch.set_num_threads(args.threads)
    dataset,entries=load_entries(args.dataset)
    endpoints=dataset.get('endpoints',{})
    pinned={**({'LiCoO2':str(endpoints['electrode']['material_id']),'Li6PS5Cl':str(endpoints['electrolyte']['material_id'])}
               if endpoints else {}),**COATINGS,**dict(e.split('=',1) for e in args.extra)}
    if args.only:pinned={k:v for k,v in pinned.items() if k in args.only}
    model='upet:pet-mad-s@1.6.0'
    checkpoint_sha256=None
    if args.checkpoint:
        if args.checkpoint.name!='pet-mad-s-v1.6.0.ckpt':
            ap.error('Checkpoint filename must identify the pinned PET-MAD S 1.6.0 model')
        from upet.ase import UPETCalculator
        checkpoint_sha256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest()
        inner=UPETCalculator(checkpoint_path=str(args.checkpoint),device='cpu')
    else:
        inner=load_mlip(model,device='cpu')
    calc=CountedCalculator(inner)
    started=time.monotonic();results={}
    for formula,mid in pinned.items():
        structure=SpacegroupAnalyzer(resolve_entry(entries,mid).structure).get_conventional_standard_structure()
        atoms=AseAtomsAdaptor.get_atoms(structure)
        atoms.set_initial_magnetic_moments(None)
        out=args.output/formula
        print(f'{formula} ({mid}): {len(atoms)} atoms',flush=True)
        final,record=relax_cell_record(atoms,calc,out/'symmetric',fmax=args.fmax,smax_GPa=args.smax,steps=args.steps)
        print(f'  symmetric: converged={record["converged"]}, steps={record["steps"]}, rounds={record["optimizer_rounds"]}, '
              f'fmax={record["final"]["max_force_eV_A"]:.4f} (raw {record["final"]["max_raw_force_eV_A"]:.4f}), '
              f'smax={record["final"]["max_abs_stress_GPa"]:.4f} GPa',flush=True)
        rattled=final.copy();rattled.rattle(stdev=args.rattle,seed=0)
        _,check=relax_cell_record(rattled,calc,out/'stability_check',fmax=args.fmax,smax_GPa=args.smax,
                                  steps=args.steps,symmetry=False)
        drop=(check['final']['energy_eV']-record['final']['energy_eV'])/len(final)*1000
        print(f'  stability check: converged={check["converged"]}, dE={drop:+.3f} meV/atom, '
              f'space group {check["final"]["space_group"]}',flush=True)
        mp=np.array(structure.lattice.parameters);relaxed=final.cell.cellpar()
        AseAtomsAdaptor.get_structure(final).to(filename=str(out/'relaxed.cif'))
        results[formula]={'material_id':mid,'symmetric':record,'stability_check':check,
            'stability_rattle_A':args.rattle,'stability_dE_meV_per_atom':drop,
            'mp_cellpar':mp.tolist(),'relaxed_cellpar':relaxed.tolist(),
            'lattice_change_percent':((relaxed[:3]/mp[:3]-1)*100).tolist(),
            'volume_change_percent':(final.get_volume()/structure.volume-1)*100}
        (args.output/'summary.json').write_text(json.dumps(dict(model=model,checkpoint_sha256=checkpoint_sha256,
            dataset_sha256=dataset['sha256'],cell='conventional standard (pymatgen)',optimizer='FIRE + FrechetCellFilter',
            fmax_eV_A=args.fmax,smax_GPa=args.smax,step_limit=args.steps,torch_threads=args.threads,device='cpu',
            packages={p:version(p) for p in ['upet','torch','ase','pymatgen','pymatgen-core']},
            calculator_calls=calc.calls,calculator_wall_seconds=calc.wall_seconds,
            wall_seconds=time.monotonic()-started,materials=results),indent=2,allow_nan=False)+'\n')
    print(f'Done: {calc.calls} calculator calls, {time.monotonic()-started:.1f} s',flush=True)

if __name__=='__main__':main()
