#!/usr/bin/env python3
"""Run a prepared sharp-interface pilot, with explicit convergence and accounting."""
import argparse
import copy
from importlib.metadata import version
import json
import hashlib
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from ase.io import write
from pymatgen.core.interface import Interface
from pymatgen.io.ase import AseAtomsAdaptor
from interphaise.tools.energetics import to_atoms,bottom_fixed_indices,EV_PER_A2_TO_J_PER_M2
from interphaise.tools.mlip import load_mlip
from interphaise.tools.relaxation import CountedCalculator,relax_record
from interphaise.tools.validation import _min_distance_violations


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,default=ROOT/'runs/petmad_interface_pilot')
    ap.add_argument('--output',type=Path,default=ROOT/'runs/petmad_interface_pilot/calculation')
    ap.add_argument('--checkpoint',type=Path,help='Optional cached pet-mad-s-v1.6.0.ckpt for fully offline loading')
    ap.add_argument('--steps',type=int,default=400)
    ap.add_argument('--fmax',type=float,default=.05)
    fix=ap.add_mutually_exclusive_group()
    fix.add_argument('--fixed-fraction',type=float,help='Bottom fraction of the substrate z span held fixed (default 0.34)')
    fix.add_argument('--fixed-depth',type=float,help='Bottom depth of the substrate held fixed, Å; constant when the slab is thickened')
    ap.add_argument('--registry',type=float,nargs=3,metavar=('X','Y','GAP'),
                    help='Use this registry instead of the scan optimum; the scan is still run and saved')
    ap.add_argument('--threads',type=int,default=2)
    args=ap.parse_args()
    if args.output.exists():ap.error('Use a fresh calculation output directory')
    args.output.mkdir(parents=True)
    import torch
    torch.set_num_threads(args.threads)
    started=time.monotonic()
    interface=Interface.from_dict(json.loads((args.input/'interface.json').read_text()))
    selected=json.loads((args.input/'selected.json').read_text())
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
    scan=[]
    for x in (0,.5):
        for y in (0,.5):
            for gap in (2.,2.5,3.):
                trial=copy.deepcopy(interface);trial.in_plane_offset=(x,y);trial.gap=gap
                clashes=_min_distance_violations(trial)
                if clashes:
                    scan.append({'offset':[x,y],'gap_A':gap,'status':'rejected','clashes':clashes})
                    continue
                atoms=to_atoms(trial);atoms.calc=calc
                energy=float(atoms.get_potential_energy())
                if not np.isfinite(energy):raise ValueError('Nonfinite registry energy')
                scan.append({'offset':[x,y],'gap_A':gap,'energy_eV':energy,'status':'ok'})
                print(f'Registry {x},{y}, gap {gap}: {energy:.6f} eV',flush=True)
    scan_best=min((r for r in scan if r['status']=='ok'),key=lambda r:r['energy_eV'])
    best=scan_best
    if args.registry:
        x,y,gap=args.registry
        best=next(r for r in scan if r['offset']==[x,y] and r['gap_A']==gap and r['status']=='ok')
        if best is not scan_best:print(f'Registry fixed at {best["offset"]}, {best["gap_A"]} Å; scan optimum differs: {scan_best["offset"]}, {scan_best["gap_A"]} Å',flush=True)
    interface.in_plane_offset=best['offset'];interface.gap=best['gap_A']
    start=to_atoms(interface)
    write(args.output/'initial.extxyz',start)
    (args.output/'registry_scan.json').write_text(json.dumps(scan,indent=2)+'\n')
    fraction=.34 if args.fixed_fraction is None and args.fixed_depth is None else args.fixed_fraction
    fixed=bottom_fixed_indices(start,interface.substrate_indices,fraction,depth=args.fixed_depth)
    zs={name:start.positions[list(idx),2] for name,idx in (('film',interface.film_indices),('substrate',interface.substrate_indices))}
    film_indices=list(interface.film_indices);sub_indices=list(interface.substrate_indices)
    separated={'interface':(start,fixed),'film':(start[film_indices],[]),
               'substrate':(start[sub_indices],[sub_indices.index(i) for i in fixed])}
    records={};finals={}
    for name,(atoms,frozen) in separated.items():
        print(f'Relaxing {name}: {len(atoms)} atoms, {len(frozen)} fixed',flush=True)
        final,record=relax_record(atoms,calc,args.output/name,fixed=frozen,fmax=args.fmax,steps=args.steps)
        record['overlap_violations']=_min_distance_violations(AseAtomsAdaptor.get_structure(final))
        records[name]=record;finals[name]=final
        (args.output/'relaxation_records.json').write_text(json.dumps(records,indent=2)+'\n')
        print(f'{name}: converged={record["converged"]}, steps={record["steps"]}, fmax={record["max_free_force_eV_A"]:.5f}',flush=True)
    area=float(np.linalg.norm(np.cross(start.cell[0],start.cell[1])))
    candidate_w=(records['film']['final_energy_eV']+records['substrate']['final_energy_eV']-
                 records['interface']['final_energy_eV'])/area*EV_PER_A2_TO_J_PER_M2
    valid=all(r['converged'] and not r['overlap_violations'] for r in records.values())
    result={'model':model,'checkpoint_sha256':checkpoint_sha256,'device':'cpu','torch_threads':args.threads,'purpose':'one-contact finite-cell pilot',
        'fixed_fraction':fraction,'fixed_depth_A':args.fixed_depth,'n_fixed':len(fixed),'fixed_indices':fixed,
        'slab_z_span_A':{k:float(np.ptp(v)) for k,v in zs.items()},
        'registry_fixed':args.registry,'registry_scan_optimum':scan_best,'registry_scan_optimum_used':best is scan_best,
        'selected':selected,'area_A2':area,'n_atoms':len(start),'registry_points':len(scan),
        'best_registry':best,'relaxations':records,'numerically_valid':valid,
        'status':'converged_pilot' if valid else 'unconverged_or_invalid',
        'work_of_adhesion_J_m2':candidate_w if valid else None,
        'unvalidated_energy_difference_J_m2':candidate_w,
        'calculator_calls':calc.calls,'calculator_wall_seconds':calc.wall_seconds,
        'wall_seconds':time.monotonic()-started,
        'packages':{p:version(p) for p in ['upet','torch','ase','pymatgen','pymatgen-core']},
        'limitations':['One sharp contact, not both sides of the coating.',
          'Fixed in-plane cell; no thickness, vacuum, termination or facet convergence study.',
          'Formal polar-slab warnings remain; the model is a finite-range MLIP.',
          'Neutral stoichiometric atomistic calculation; no explicit applied voltage or electron reservoir.',
          'Separate slab references relaxed from the same registry/cell with the same substrate constraints.',
          'Numerical convergence does not validate chemical accuracy or transport.']}
    (args.output/'result.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ['status','work_of_adhesion_J_m2','calculator_calls','wall_seconds']},indent=2))

if __name__=='__main__':main()
