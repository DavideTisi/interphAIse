#!/usr/bin/env python3
"""Fill the campaign index from a gated primary-feedback bundle (build_primary_feedback.py).

Only runs whose status the bundle decided are written; values come from the bundle (which
recomputed them), never from the raw files directly. Job IDs come from a saved `sacct` listing.
Pending/unknown entries and every other run stay untouched.
"""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--index',type=Path,default=ROOT/'data/petmad/coating_comparison_v1/index.json')
    ap.add_argument('--bundle',type=Path,required=True);ap.add_argument('--sacct',type=Path)
    ap.add_argument('--source-commit',required=True)
    ap.add_argument('--slot-reason',required=True,choices=['reference','llm_choice_2','llm_choice_3','fixed','fallback'])
    args=ap.parse_args()
    index=json.loads(args.index.read_text());bundle=json.loads(args.bundle.read_text())
    if bundle['manifest_sha256']!=index['manifest_sha256']:sys.exit('bundle and index were built from different manifests')
    jobs={}
    if args.sacct:
        for line in args.sacct.read_text().splitlines():
            parts=line.split()
            if len(parts)>=2:jobs[parts[1].split('-',1)[-1]]=parts[0]   # name like LiTaF6-cathode_R1
    cid=bundle['coating']['candidate_id'];rows={r['run_id']:r for r in index['runs']};updated=[]
    for contact,spec in bundle['contacts'].items():
        for reg in spec['registries']:
            if reg['status']=='pending':continue
            run_id=f"{cid}:{contact}:primary:{reg['registry_id']}"
            if run_id not in rows:sys.exit(f'{run_id} is not in the index')
            run=Path(reg['run']);row=rows[run_id]
            row.update(status=reg['status'],failure_reason=reg.get('failure'),W_adh_J_m2=reg['W_adh_J_m2'],W_sep_J_m2=reg['W_sep_J_m2'],
                joined_energy_eV=reg.get('joined_energy_eV'),result_path=str(run/'result.json'),result_sha256=sha(run/'result.json'),
                separation_path=str(run/'fixed_geometry_separation.json') if (run/'fixed_geometry_separation.json').exists() else None,
                separation_single_points=reg.get('separation_single_points',0),device=reg.get('device'),
                calculator_calls=reg.get('calculator_calls'),wall_seconds=reg.get('wall_seconds'),
                job_id=jobs.get(f"{contact}_{reg['registry_id']}"),source_commit=args.source_commit,
                warnings=[f"formal polarity film/substrate {spec['build']['formal_polarity_e_per_A']['film']:.3f}/"
                          f"{spec['build']['formal_polarity_e_per_A']['substrate']:.3f} e/Å"])
            updated.append(run_id)
    index.setdefault('cohort',[])
    if not any(c['candidate_id']==cid for c in index['cohort']):index['cohort'].append({'candidate_id':cid,'slot_reason':args.slot_reason})
    index['last_bundle']={'candidate_id':cid,'bundle':str(args.bundle),'bundle_sha256':sha(args.bundle),
                          'consumable_by_agent':bundle['consumable_by_agent']}
    args.index.write_text(json.dumps(index,indent=1)+'\n')
    print(f'updated {len(updated)} rows for {cid}; index sha256 {sha(args.index)[:16]}')

if __name__=='__main__':main()
