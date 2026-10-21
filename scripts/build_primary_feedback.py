#!/usr/bin/env python3
"""Assemble the frozen two-contact `primary_feedback` bundle for one coating.

Schema `petmad-primary-feedback-v2`. The coating's entry in the frozen campaign manifest is the
contract: it lists, per contact, the expected build (candidate pair/facets/termination, atom
count, area, composition, fixed-atom count and species) and the planned registries (ID,
offset, gap). Runs are supplied as REGISTRY_ID=DIR and are accepted only if:

* coverage is exact: every planned registry appears once, no unplanned or duplicate IDs/dirs;
  a planned registry without a run is `pending` and makes the bundle **non-consumable**;
* the run is comparable: F2 provenance (checkpoint, convergence, labels, cell/area), the
  requested registry, force target/step limit, candidate/contact identity, atom count, area,
  composition and physical fixed mask all match the manifest (labels on the command line are
  never trusted on their own);
* the numbers are consistent: W_adh is recomputed from the saved energies and area; W_sep from
  the rigid-fragment energies, with checkpoint, joined energy and area matched to the run.

Two kinds of non-valid run are kept apart, both with null works, known cost and reason:
`failed` is a genuine completed calculation failure (unconverged/non-finite relaxation, overlaps);
it is reported as feedback and consumes the slot. `invalid_evidence` is a broken or inconsistent
package (wrong checkpoint, tampered or mismatched numbers, files, identity, cell, mask or registry,
missing separation); it **blocks** consumption (`consumable_by_agent: false`) until resolved. Selection per contact: lowest relaxed joined energy among valid runs. Sensitivity
checks are listed as pending/not_run with null values and never enter this bundle.
"""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
from ase.geometry import find_mic
from interphaise.tools.energetics import EV_PER_A2_TO_J_PER_M2
from interphaise.tools.provenance import load_valid_interface_run,ProvenanceError

SCHEMA='petmad-primary-feedback-v2'
TOLERANCE=0.1           # J/m², reporting convention only (LLM_PETMAD_PILOT_PLAN.md)
ARITHMETIC_TOL=1e-6     # J/m², recomputation tolerance
LIMITATIONS=[
    'PET-MAD S 1.6.0 is a finite-range (8 Å neighbour list) MLIP: no explicit long-range electrostatics.',
    'Contacts use formally polar slabs; polar-surface energy errors are not quantified.',
    'Neutral, fixed-stoichiometry cells: no applied voltage, electron reservoir or Li exchange.',
    'Two separately matched strained contact cells, not one continuous coating film.',
    'Ordered bulk approximants; no disorder ensemble. No Li transport or kinetics.',
    'Primary registries are a coarse geometric sample, not a global registry search.',
]


class FeedbackError(ValueError):
    """The supplied runs cannot form a bundle under the manifest contract."""


def work(e_film,e_sub,e_int,area):
    return (e_film+e_sub-e_int)/area*EV_PER_A2_TO_J_PER_M2


def check_run(run,plan,expected,protocol):
    """Return (record, problems). Problems make the run a failed outcome."""
    valid=load_valid_interface_run(run,protocol['checkpoint_sha256'])
    r=valid['result'];R=r['relaxations'];problems=[]
    reg=r.get('registry_fixed')
    if reg is None or not np.allclose(reg,[*plan['offset'],plan['gap_A']],atol=1e-9):
        problems.append(f"registry {reg} is not the planned {[*plan['offset'],plan['gap_A']]}")
    for name,rec in R.items():
        if rec.get('fmax_target_eV_A')!=protocol['force_target_eV_A'] or rec.get('step_limit')!=protocol['step_limit']:
            problems.append(f'{name} relaxation used a different force target/step limit')
    cand=(r.get('selected') or {}).get('candidate',{})
    for key in ('pair','film_miller','substrate_miller','termination'):
        if [*cand.get(key,[])]!=[*expected['candidate'][key]]:
            problems.append(f"{key} {cand.get(key)} differs from the manifest {expected['candidate'][key]}")
    joined=valid['finals']['interface']
    if len(joined)!=expected['n_atoms']:problems.append(f"{len(joined)} atoms, manifest {expected['n_atoms']}")
    if not np.isclose(valid['area_A2'],expected['area_A2'],rtol=1e-6):problems.append(f"area {valid['area_A2']:.4f} Å² differs")
    if joined.get_chemical_formula()!=expected['formula']:problems.append(f'composition {joined.get_chemical_formula()} differs')
    fixed=R['interface'].get('fixed_atom_indices',[])
    fixed_species=dict(sorted({s:[joined[i].symbol for i in fixed].count(s) for s in {joined[i].symbol for i in fixed}}.items()))
    if len(fixed)!=expected['n_fixed'] or fixed_species!=expected['fixed_species']:
        problems.append(f'fixed mask {len(fixed)} {fixed_species} differs from {expected["n_fixed"]} {expected["fixed_species"]}')
    # Arithmetic: recompute rather than trust stored totals.
    area=valid['area_A2'];energies={k:R[k]['final_energy_eV'] for k in R}
    w_adh=work(energies['film'],energies['substrate'],energies['interface'],area)
    if abs(w_adh-r['work_of_adhesion_J_m2'])>ARITHMETIC_TOL:
        problems.append(f"stored W_adh {r['work_of_adhesion_J_m2']} != recomputed {w_adh:.6f}")
    sep_path=Path(run)/'fixed_geometry_separation.json';w_sep=None;sep_relax={'film':None,'substrate':None}
    if not sep_path.exists():
        sep_status='missing';problems.append('separation file missing: the primary package is incomplete')
    else:
        try:sep=json.loads(sep_path.read_text())
        except json.JSONDecodeError:sep={}
        sep_problems=[]
        if sep.get('checkpoint_sha256')!=protocol['checkpoint_sha256']:sep_problems.append('checkpoint')
        if sep.get('E_interface_eV')!=energies['interface']:sep_problems.append('joined energy')
        if not np.isclose(sep.get('area_A2',np.nan),area,rtol=1e-9):sep_problems.append('area')
        rigid=[sep.get('E_film_rigid_eV',np.nan),sep.get('E_substrate_rigid_eV',np.nan)]
        finite=bool(np.all(np.isfinite(rigid)))
        if finite and abs(work(rigid[0],rigid[1],energies['interface'],area)-sep.get('W_sep_fixed_geometry_J_m2',np.nan))>ARITHMETIC_TOL:
            sep_problems.append('W_sep arithmetic')
        if sep_problems:   # an inconsistent separation file is invalid evidence, not a chemistry outcome
            sep_status='invalid_evidence: '+', '.join(sep_problems);problems.append('separation '+sep_status)
        elif not finite:sep_status='failed_calculation: non-finite rigid-fragment energy'
        else:
            sep_status='valid';w_sep=work(rigid[0],rigid[1],energies['interface'],area)
            sep_relax={p:(sep[f'E_{p}_rigid_eV']-energies[p])/area*EV_PER_A2_TO_J_PER_M2 for p in ('film','substrate')}
    labels=valid['labels'];reconstruction={}
    for part in ('film','substrate'):
        idx=np.where(labels==part)[0];sep_atoms=valid['finals'][part]
        d=np.linalg.norm(find_mic(sep_atoms.positions-joined[idx].positions,joined.cell,joined.pbc)[0],axis=1)
        sym=np.array(sep_atoms.get_chemical_symbols())
        reconstruction[part]={e:round(float(np.sqrt((d[sym==e]**2).mean())),3) for e in sorted(set(sym))}
    record={'joined_energy_eV':energies['interface'],'W_adh_J_m2':w_adh,'W_sep_J_m2':w_sep,'separation_status':sep_status,
        'separated_relaxation_J_m2':sep_relax,
        'relaxations':{k:{'converged':v['converged'],'steps':v['steps'],'max_free_force_eV_A':v['max_free_force_eV_A'],
                          'max_raw_force_all_atoms_eV_A':v['max_unconstrained_force_eV_A']} for k,v in R.items()},
        'n_atoms':len(joined),'area_A2':area,'n_fixed':len(fixed),'fixed_species':fixed_species,
        'separated_minus_joined_rms_displacement_A':reconstruction,'device':r.get('device'),
        'calculator_calls':r['calculator_calls'],'separation_single_points':2 if sep_status=='valid' else 0,
        'wall_seconds':r['wall_seconds']}
    return record,problems


def known_cost(run):
    """Cost of a run that failed validation, if its files record it (else unknown/None)."""
    try:r=json.loads((Path(run)/'result.json').read_text())
    except (FileNotFoundError,json.JSONDecodeError):return None,None
    return r.get('calculator_calls'),r.get('wall_seconds')


def assemble(manifest,coating_id,runs):
    entry=manifest['coatings'][coating_id];protocol=manifest['protocol']
    planned={(c,p['id']):p for c,spec in entry['contacts'].items() for p in spec['registries']}
    supplied={}
    for (contact,rid),path in runs:
        if (contact,rid) not in planned:raise FeedbackError(f'{contact}/{rid} is not a planned registry')
        if (contact,rid) in supplied:raise FeedbackError(f'duplicate run for {contact}/{rid}')
        if path in supplied.values():raise FeedbackError(f'{path} supplied for more than one registry')
        supplied[(contact,rid)]=path
    contacts={};failures=[];blocking=[];costs={'new_jobs':0,'reused_jobs':0,'calculator_calls_known':0,'separation_single_points':0,
                                    'wall_seconds_known':0.0,'runs_with_unknown_cost':0,'pending_jobs':0}
    for contact,spec in entry['contacts'].items():
        recs=[]
        for plan in spec['registries']:
            base={'registry_id':plan['id'],'offset':plan['offset'],'gap_A':plan['gap_A'],'reused':bool(plan.get('reused_from'))}
            path=supplied.get((contact,plan['id']))
            if path is None:
                recs.append(base|{'status':'pending','W_adh_J_m2':None,'W_sep_J_m2':None});costs['pending_jobs']+=1;continue
            costs['reused_jobs' if base['reused'] else 'new_jobs']+=1
            kind='integrity'
            try:record,problems=check_run(path,plan,spec['expected'],protocol)
            except ProvenanceError as error:record,problems,kind=None,[str(error)],error.kind
            except (FileNotFoundError,KeyError,json.JSONDecodeError) as error:record,problems=None,[str(error)]
            if problems:
                # 'failed': a genuine completed calculation failure (reported, consumes the slot).
                # 'invalid_evidence': the package is broken or inconsistent; it blocks consumption until resolved.
                status='failed' if kind=='calculation' else 'invalid_evidence'
                calls,wall=known_cost(path)
                recs.append(base|{'status':status,'failure':'; '.join(problems),'run':str(path),'W_adh_J_m2':None,'W_sep_J_m2':None,
                                  'calculator_calls':calls,'wall_seconds':wall})
                (failures if status=='failed' else blocking).append({'contact':contact,'registry_id':plan['id'],'reason':'; '.join(problems)})
                if calls is None:costs['runs_with_unknown_cost']+=1
                else:costs['calculator_calls_known']+=calls;costs['wall_seconds_known']+=wall or 0
                continue
            recs.append(base|{'status':'valid','run':str(path)}|record)
            costs['calculator_calls_known']+=record['calculator_calls'];costs['wall_seconds_known']+=record['wall_seconds']
            costs['separation_single_points']+=record['separation_single_points']
        valid=[r for r in recs if r['status']=='valid']
        if valid:
            emin=min(r['joined_energy_eV'] for r in valid)
            for r in valid:r['joined_energy_above_lowest_eV']=r['joined_energy_eV']-emin
            best=min(valid,key=lambda r:r['joined_energy_eV'])
            selected={'registry_id':best['registry_id'],'W_adh_J_m2':best['W_adh_J_m2'],'W_sep_J_m2':best['W_sep_J_m2']}
            rng={k:([min(v),max(v)] if (v:=[r[k] for r in valid if r[k] is not None]) else None) for k in ('W_adh_J_m2','W_sep_J_m2')}
        else:
            selected={'registry_id':None,'W_adh_J_m2':None,'W_sep_J_m2':None};rng={'W_adh_J_m2':None,'W_sep_J_m2':None}
        contacts[contact]={'build':spec['expected'],'registries':recs,'selected':selected,'registry_range':rng,
                           'n_planned':len(spec['registries']),'n_valid':len(valid),
                           'n_failed':sum(r['status']=='failed' for r in recs),'n_pending':sum(r['status']=='pending' for r in recs),
                           'n_invalid_evidence':sum(r['status']=='invalid_evidence' for r in recs)}
    consumable=costs['pending_jobs']==0 and not blocking
    w={c:contacts[c]['selected']['W_adh_J_m2'] for c in contacts}
    if not consumable or None in w.values():weaker,gap,wmin='unresolved',None,None
    else:
        gap=abs(w['cathode']-w['electrolyte']);wmin=min(w.values())
        weaker='unresolved' if gap<TOLERANCE else min(w,key=w.get)
    return {'schema':SCHEMA,'consumable_by_agent':consumable,
        'coating':{'candidate_id':coating_id,'formula':entry['formula']},
        'manifest_sha256':manifest.get('_sha256'),'protocol':protocol,'contacts':contacts,
        'summary':{'weaker_contact':weaker,'min_W_adh_J_m2':wmin,'W_adh_gap_J_m2':gap,'tolerance_J_m2':TOLERANCE},
        'sensitivity':{**{k:{'status':v,'value':None} for k,v in entry.get('sensitivity',{}).items()},
                       **{f'{c}:{k}':{'status':v['status'],'reason':v.get('reason'),'value':None}
                          for c,spec in entry['contacts'].items() for k,v in spec.get('sensitivity',{}).items()}},
        'observed_failures':failures,'blocking_integrity_issues':blocking,'model_limitations':LIMITATIONS,'costs':costs}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest',type=Path,required=True);ap.add_argument('--coating',required=True,help='Candidate ID')
    ap.add_argument('--run',nargs=2,action='append',default=[],metavar=('CONTACT','REGISTRY_ID=DIR'))
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    text=args.manifest.read_text();manifest=json.loads(text);manifest['_sha256']=hashlib.sha256(text.encode()).hexdigest()
    runs=[((c,s.split('=',1)[0]),s.split('=',1)[1]) for c,s in args.run]
    try:bundle=assemble(manifest,args.coating,runs)
    except FeedbackError as error:ap.error(str(error))
    out=json.dumps(bundle,indent=1,allow_nan=False)+'\n'
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(out)
    digest=hashlib.sha256(out.encode()).hexdigest();Path(str(args.output)+'.sha256').write_text(digest+'\n')
    print(f"{args.output}: consumable={bundle['consumable_by_agent']} weaker={bundle['summary']['weaker_contact']} "
          f"min_W_adh={bundle['summary']['min_W_adh_J_m2']} failures={len(bundle['observed_failures'])} sha256={digest[:16]}")

if __name__=='__main__':main()
