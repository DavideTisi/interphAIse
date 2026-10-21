#!/usr/bin/env python3
"""Multistart unconstrained relaxations around a saved symmetric bulk minimum.

Seeds 1..N rattle the saved symmetric cell exactly as relax_bulk.py made seed 0 (sigma,
seed) and relax positions + lattice without symmetry, same force/stress targets and step
budget. Seed 0 is read back from the bulk run, not recomputed. Exhausted runs are kept and
reported, never extended silently. This probes nearby basins only, not Li/S/Cl disorder.
"""
import argparse
import numpy as np
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ase.io import read
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.io.ase import AseAtomsAdaptor
from interphaise.tools.relaxation import CountedCalculator,relax_cell_record,space_group
from interphaise.tools.validation import _min_distance_violations
from interphaise.tools.provenance import checkpoint_sha256,require_matching_checkpoint,ProvenanceError
from inspect_bulk_relaxation import CHECKS,coordination


def describe(atoms):
    structure=AseAtomsAdaptor.get_structure(atoms)
    return {'cellpar':atoms.cell.cellpar().tolist(),'volume_A3':float(atoms.get_volume()),
            'overlap_violations':_min_distance_violations(structure),
            'min_distance_A':float(min(atoms.get_distance(i,j,mic=True) for i in range(len(atoms)) for j in range(i))),
            'space_group':{p:space_group(atoms,p) for p in (1e-3,1e-2,1e-1)}}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('material')
    ap.add_argument('--bulk',type=Path,default=ROOT/'data/petmad/bulk_relaxation_v1')
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--seeds',type=int,nargs='+',default=[1,2,3,4,5])
    ap.add_argument('--rattle',type=float,default=.02)
    ap.add_argument('--fmax',type=float,default=.01)
    ap.add_argument('--smax',type=float,default=.05)
    ap.add_argument('--steps',type=int,default=1000)
    ap.add_argument('--threads',type=int,default=2)
    args=ap.parse_args()
    if args.output.exists():ap.error('Use a fresh output directory')
    if args.checkpoint.name!='pet-mad-s-v1.6.0.ckpt':ap.error('Checkpoint must be the pinned PET-MAD S 1.6.0 file')
    # F2: new seed energies are compared with saved ones, so the saved bulk run must use this exact checkpoint
    # and its symmetric reference must have converged. Checked before loading the model or writing output.
    sha=checkpoint_sha256(args.checkpoint)
    summary=json.loads((args.bulk/'summary.json').read_text())
    try:require_matching_checkpoint(sha,{'bulk summary.json':summary.get('checkpoint_sha256')})
    except ProvenanceError as error:ap.error(str(error))
    bulk=summary['materials'][args.material]
    if not bulk['symmetric']['converged'] or not np.isfinite(bulk['symmetric']['final']['energy_eV']):
        ap.error(f'{args.material}: saved symmetric reference is unconverged or non-finite')
    args.output.mkdir(parents=True)
    import torch
    torch.set_num_threads(args.threads)
    from upet.ase import UPETCalculator
    calc=CountedCalculator(UPETCalculator(checkpoint_path=str(args.checkpoint),device='cpu'))
    symmetric=read(args.bulk/args.material/'symmetric/final.extxyz')
    e_sym=bulk['symmetric']['final']['energy_eV'];n=len(symmetric)
    runs={0:{'source':'bulk run stability check (not recomputed)','converged':bulk['stability_check']['converged'],
             'steps':bulk['stability_check']['steps'],'energy_eV':bulk['stability_check']['final']['energy_eV'],
             'structure':read(args.bulk/args.material/'stability_check/final.extxyz')}}
    started=time.monotonic()
    for seed in args.seeds:
        start=symmetric.copy();start.rattle(stdev=args.rattle,seed=seed)
        final,record=relax_cell_record(start,calc,args.output/f'seed_{seed}',fmax=args.fmax,smax_GPa=args.smax,
                                       steps=args.steps,symmetry=False)
        runs[seed]={'source':'this run','converged':record['converged'],'steps':record['steps'],
                    'energy_eV':record['final']['energy_eV'],'record':record,'structure':final}
        print(f'{args.material} seed {seed}: converged={record["converged"]}, steps={record["steps"]}, '
              f'dE={(record["final"]["energy_eV"]-e_sym)/n*1000:+.3f} meV/atom',flush=True)
    # Group converged minima into basins; unconverged runs are listed but never grouped or selected.
    matcher=StructureMatcher()
    pmg={s:AseAtomsAdaptor.get_structure(r['structure']) for s,r in runs.items()}
    basins=[]
    for s in sorted((s for s,r in runs.items() if r['converged']),key=lambda s:runs[s]['energy_eV']):
        for b in basins:
            if matcher.fit(pmg[b[0]],pmg[s]):b.append(s);break
        else:basins.append([s])
    out={'material':args.material,'material_id':bulk['material_id'],'checkpoint_sha256':sha,'n_atoms':n,
         'symmetric_energy_eV':e_sym,'rattle_A':args.rattle,'fmax_eV_A':args.fmax,'smax_GPa':args.smax,
         'step_limit':args.steps,'torch_threads':args.threads,'calculator_calls':calc.calls,
         'wall_seconds':time.monotonic()-started,
         'structure_matcher':{'ltol':matcher.ltol,'stol':matcher.stol,'angle_tol':matcher.angle_tol},
         'seeds':{},'basins':[]}
    for s,r in sorted(runs.items()):
        info=describe(r['structure'])
        info['coordination']={f'{c}-{l}<{cut}':coordination(r['structure'],c,l,cut) for c,l,cut in CHECKS.get(args.material,[])}
        out['seeds'][str(s)]={k:v for k,v in r.items() if k not in ('structure','record')}|{
            'dE_vs_symmetric_meV_per_atom':(r['energy_eV']-e_sym)/n*1000,**info}
        if 'record' in r:out['seeds'][str(s)]['max_force_eV_A']=r['record']['final']['max_force_eV_A'];out['seeds'][str(s)]['max_abs_stress_GPa']=r['record']['final']['max_abs_stress_GPa']
    for b in basins:
        out['basins'].append({'seeds':b,'lowest_seed':b[0],'dE_vs_symmetric_meV_per_atom':out['seeds'][str(b[0])]['dE_vs_symmetric_meV_per_atom']})
    (args.output/'multistart.json').write_text(json.dumps(out,indent=2)+'\n')
    print(f'{args.material}: {len(basins)} basin(s) among converged seeds: '
          +'; '.join(f"seeds {b['seeds']} at {b['dE_vs_symmetric_meV_per_atom']:+.2f} meV/atom" for b in out['basins']),flush=True)

if __name__=='__main__':main()
