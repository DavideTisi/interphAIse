#!/usr/bin/env python3
"""Assemble the frozen two-contact `primary_feedback` bundle for one coating (schema below).

Inputs are completed run_petmad_interface.py directories (one per primary registry and
contact) plus their fixed_geometry_separation.json. Each run is checked with the F2 gate;
a run that fails validation is kept as a failed outcome with null works, never dropped.
The selected registry per contact is the lowest relaxed joined energy among valid runs
(same cell/composition/mask by construction). Sensitivity checks are listed as pending:
their numbers never enter this bundle. Output: <output>.json and its SHA-256.

Schema `petmad-primary-feedback-v1` (missing or invalid quantities are null):
  coating{candidate_id, formula}, protocol{checkpoint_sha256, model, force_target_eV_A,
  step_limit, gates}, contacts{cathode|electrolyte: {build, registries[...], selected,
  registry_range, n_planned, n_valid}}, summary{weaker_contact, min_W_adh_J_m2,
  W_adh_gap_J_m2, tolerance_J_m2}, sensitivity{...: pending}, observed_failures[],
  model_limitations[], costs{}, sources[].
"""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from ase.geometry import find_mic
from interphaise.tools.provenance import load_valid_interface_run,ProvenanceError

TOLERANCE=0.1   # J/m², reporting convention only (LLM_PETMAD_PILOT_PLAN.md)
LIMITATIONS=[
    'PET-MAD S 1.6.0 is a finite-range (8 Å neighbour list) MLIP: no explicit long-range electrostatics.',
    'Both contacts use formally polar slabs; polar-surface energy errors are not quantified.',
    'Neutral, fixed-stoichiometry cells: no applied voltage, electron reservoir or Li exchange.',
    'Two separately matched strained contact cells, not one continuous coating film.',
    'Ordered bulk approximants; no disorder ensemble. No Li transport or kinetics.',
    'Primary registries are a coarse sample, not a global registry search.',
]


def run_record(run,sha,contact,offset_label):
    rec={'contact':contact,'registry':offset_label,'run':str(run),'status':'failed','failure':None}
    try:valid=load_valid_interface_run(run,sha)
    except (ProvenanceError,FileNotFoundError,KeyError) as error:
        rec['failure']=str(error);rec.update(W_adh_J_m2=None,W_sep_J_m2=None,joined_energy_eV=None);return rec
    r=valid['result'];R=r['relaxations']
    try:sep=json.loads((Path(run)/'fixed_geometry_separation.json').read_text())
    except FileNotFoundError:sep=None
    sep_ok=sep is not None and sep.get('checkpoint_sha256')==sha and np.isfinite(sep.get('W_sep_fixed_geometry_J_m2',np.nan))
    labels=valid['labels'];joined=valid['finals']['interface']
    reconstruction={}
    for part in ('film','substrate'):
        idx=np.where(labels==part)[0];sep_atoms=valid['finals'][part]
        d=np.linalg.norm(find_mic(sep_atoms.positions-joined[idx].positions,joined.cell,joined.pbc)[0],axis=1)
        sym=np.array(sep_atoms.get_chemical_symbols())
        reconstruction[part]={e:round(float(np.sqrt((d[sym==e]**2).mean())),3) for e in sorted(set(sym))}
    rec.update(status='valid',joined_energy_eV=R['interface']['final_energy_eV'],
        W_adh_J_m2=r['work_of_adhesion_J_m2'],W_sep_J_m2=sep['W_sep_fixed_geometry_J_m2'] if sep_ok else None,
        separation_status='valid' if sep_ok else 'missing_or_invalid',
        separated_relaxation_J_m2={p:(sep[f'{p}_relaxation_J_m2'] if sep_ok else None) for p in ('film','substrate')},
        relaxations={k:{'converged':v['converged'],'steps':v['steps'],'max_free_force_eV_A':v['max_free_force_eV_A'],
                        'max_fixed_atom_force_eV_A':v['max_unconstrained_force_eV_A']} for k,v in R.items()},
        n_atoms=r['n_atoms'],area_A2=r['area_A2'],n_fixed=r.get('n_fixed'),
        separated_minus_joined_rms_displacement_A=reconstruction,
        device=r.get('device'),calculator_calls=r['calculator_calls'],wall_seconds=r['wall_seconds'])
    return rec


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate-id',required=True);ap.add_argument('--formula',required=True)
    ap.add_argument('--checkpoint-sha256',required=True)
    ap.add_argument('--run',nargs=3,action='append',required=True,metavar=('CONTACT','REGISTRY','DIR'),
                    help="e.g. cathode '1/3,1/3' runs/x; repeat for every planned primary run")
    ap.add_argument('--build',nargs=2,action='append',default=[],metavar=('CONTACT','BUILD_JSON'))
    ap.add_argument('--planned',nargs=2,action='append',default=[],metavar=('CONTACT','N'))
    ap.add_argument('--pending',nargs='+',default=['thickness_increment','fixed_depth_variation','robustness_case'])
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    sha=args.checkpoint_sha256;builds={c:json.loads(Path(p).read_text()) for c,p in args.build}
    planned={c:int(n) for c,n in args.planned}
    contacts={};failures=[];costs={'jobs':0,'calculator_calls':0,'wall_seconds':0.0}
    for contact in ('cathode','electrolyte'):
        recs=[run_record(Path(d),sha,c,reg) for c,reg,d in args.run if c==contact]
        valid=[r for r in recs if r['status']=='valid']
        for r in recs:
            costs['jobs']+=1
            if r['status']=='valid':costs['calculator_calls']+=r['calculator_calls'];costs['wall_seconds']+=r['wall_seconds']
            else:failures.append({'contact':contact,'registry':r['registry'],'failure':r['failure']})
        if valid:
            emin=min(r['joined_energy_eV'] for r in valid)
            for r in valid:r['joined_energy_above_lowest_eV']=r['joined_energy_eV']-emin
            best=min(valid,key=lambda r:r['joined_energy_eV'])
            selected={'registry':best['registry'],'W_adh_J_m2':best['W_adh_J_m2'],'W_sep_J_m2':best['W_sep_J_m2']}
            rng={k:[min(r[k] for r in valid if r[k] is not None),max(r[k] for r in valid if r[k] is not None)]
                 if any(r[k] is not None for r in valid) else None for k in ('W_adh_J_m2','W_sep_J_m2')}
        else:
            selected={'registry':None,'W_adh_J_m2':None,'W_sep_J_m2':None};rng={'W_adh_J_m2':None,'W_sep_J_m2':None}
        b=builds.get(contact)
        contacts[contact]={'build':None if b is None else {k:b.get(k) for k in ('contact','termination','n_atoms','area_A2',
                            'von_mises_strain','film_transformation','substrate_transformation','inputs')}|{
                            'formal_polarity_e_per_A':{s:b['sides'][s]['formal_dipole_per_area_e_per_A'] for s in ('film','substrate')},
                            'cut_polyhedra':{s:b['sides'][s]['cut_polyhedra'] for s in ('film','substrate')}},
                           'registries':recs,'selected':selected,'registry_range':rng,
                           'n_planned':planned.get(contact,len(recs)),'n_valid':len(valid)}
    w={c:contacts[c]['selected']['W_adh_J_m2'] for c in contacts}
    if None in w.values():weaker,gap,wmin='unresolved',None,None
    else:
        gap=abs(w['cathode']-w['electrolyte']);wmin=min(w.values())
        weaker='unresolved' if gap<TOLERANCE else min(w,key=w.get)
    bundle={'schema':'petmad-primary-feedback-v1','coating':{'candidate_id':args.candidate_id,'formula':args.formula},
        'protocol':{'checkpoint_sha256':sha,'model':'PET-MAD S 1.6.0 (r2SCAN)','force_target_eV_A':0.05,'step_limit':400,
                    'selection':'lowest relaxed joined energy among valid primary registries, per contact',
                    'gates':'F2 provenance + all relaxations converged/finite/no overlaps'},
        'contacts':contacts,
        'summary':{'weaker_contact':weaker,'min_W_adh_J_m2':wmin,'W_adh_gap_J_m2':gap,'tolerance_J_m2':TOLERANCE},
        'sensitivity':{k:{'status':'pending','value':None} for k in args.pending},
        'observed_failures':failures,'model_limitations':LIMITATIONS,'costs':costs,
        'sources':[d for _,_,d in args.run]}
    text=json.dumps(bundle,indent=1,allow_nan=False)+'\n'
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(text)
    digest=hashlib.sha256(text.encode()).hexdigest();Path(str(args.output)+'.sha256').write_text(digest+'\n')
    print(f'{args.output}: weaker={weaker} min_W_adh={wmin} sha256={digest[:16]}')

if __name__=='__main__':main()
