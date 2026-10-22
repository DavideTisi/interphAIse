#!/usr/bin/env python3
"""Build the robustness-inclusive final comparison index after the pilot's last live call.

The decision-time indices and feedback bundles are copied unchanged into snapshots/ (hashes checked
against the live records). index.json stays exactly as the final summary saw it. index_final.json is
derived from it: primary rows and selections untouched; sensitivity, consistency and archived
reference-sensitivity rows filled from F2-validated runs with recomputed works; unselected planned
rows marked not_run_not_selected; unavailable slots kept with `quantified: false`; job accounting added.
"""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import subprocess
from interphaise.tools.energetics import EV_PER_A2_TO_J_PER_M2
from interphaise.tools.provenance import load_valid_interface_run

C=ROOT/'data/petmad/coating_comparison_v1'
SHA='3f52e97c459b2a28a94fc49b8a2f9a92551231a0ea4f5b5db2396f12d8ffa1e9'
DECISIONS=[('choose_2','b199608','b02750feffeefb0d3e7875d18bc693a3b2e4e6a5294091a21d59aee6501aa937','2026-10-22T07:40:15+00:00'),
           ('choose_3','d5ab477','4577b2ab2e9331b7161aed14120246348ec730d8ca999724150538669e2fd808','2026-10-22T08:04:25+00:00'),
           ('summary','668b5e3','7ba8cc4a7ed013017651dc7d7031a2ce9846ffae01d6f73ca81841dbdcdaf024','2026-10-22T08:54:01+00:00')]
BUNDLES={'LiTaF6':'91e80b064d3a15d305cd33640cc5838b21222852ca16cca4dc1e2459f4026da2',
         'LiCaAlF6':'2f274f1140ba447c'}   # prefix check for the second; full hash recorded from the file
ROBUSTNESS={'mp-aaacjmqp':('LiTaF6_sensitivity_v1','LiTaF6s'),'mp-aaaaajby':('LiCaAlF6_sensitivity_v1','LiCaAlF6s')}
SLOTS={'thickness':'thickness_increment','fixed_depth':'fixed_depth_variation','robustness':'robustness_case'}


def sha(b):return hashlib.sha256(b).hexdigest()


def jobs_from(sacct,prefix):
    out={}
    for line in Path(sacct).read_text().splitlines():
        p=line.split()
        if len(p)>=4:out[p[1].split('-',1)[-1]]={'job_id':p[0],'elapsed':p[3]}
    return out


def measured(run,primary=None):
    v=load_valid_interface_run(run,SHA);r=v['result'];R=r['relaxations']
    s=json.loads((Path(run)/'fixed_geometry_separation.json').read_text())
    assert s['checkpoint_sha256']==SHA and s['E_interface_eV']==R['interface']['final_energy_eV']
    w=(R['film']['final_energy_eV']+R['substrate']['final_energy_eV']-R['interface']['final_energy_eV'])/v['area_A2']*EV_PER_A2_TO_J_PER_M2
    ws=(s['E_film_rigid_eV']+s['E_substrate_rigid_eV']-R['interface']['final_energy_eV'])/v['area_A2']*EV_PER_A2_TO_J_PER_M2
    row={'status':'valid','W_adh_J_m2':w,'W_sep_J_m2':ws,'joined_energy_eV':R['interface']['final_energy_eV'],
         'n_atoms':r['n_atoms'],'area_A2':v['area_A2'],'n_fixed':r.get('n_fixed'),'registry':r.get('registry_fixed'),
         'fixed_rule':{'depth_A':r['fixed_depth_A']} if r.get('fixed_depth_A') else {'fraction':r.get('fixed_fraction')},
         'checkpoint_sha256':r['checkpoint_sha256'],'device':r.get('device'),'result_path':str(Path(run).relative_to(ROOT)/'result.json'),
         'result_sha256':sha((Path(run)/'result.json').read_bytes()),'separation_path':str(Path(run).relative_to(ROOT)/'fixed_geometry_separation.json'),
         'separation_single_points':2,'calculator_calls':r['calculator_calls'],'wall_seconds':r['wall_seconds']}
    if primary:row.update(dW_adh_vs_selected_primary_J_m2=w-primary['W_adh_J_m2'],dW_sep_vs_selected_primary_J_m2=ws-primary['W_sep_J_m2'])
    return row


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.parse_args()
    snaps=C/'snapshots';snaps.mkdir(exist_ok=True);snapshot_records=[]
    for stage,commit,expected,when in DECISIONS:
        blob=subprocess.run(['git','show',f'{commit}:data/petmad/coating_comparison_v1/index.json'],capture_output=True,check=True,cwd=ROOT).stdout
        if sha(blob)!=expected:sys.exit(f'{stage}: index at {commit} does not match the live record')
        path=snaps/f'index_{stage}_{expected[:16]}.json';path.write_bytes(blob)
        snapshot_records.append({'stage':stage,'live_record_time':when,'from_commit':commit,'index_sha256':expected,'path':str(path.relative_to(ROOT))})
    for name,expected in BUNDLES.items():
        blob=(C/f'feedback/{name}_primary_feedback.json').read_bytes()
        if not sha(blob).startswith(expected):sys.exit(f'{name} bundle changed since the decision')
        (snaps/f'{name}_primary_feedback_{sha(blob)[:16]}.json').write_bytes(blob)
        snapshot_records.append({'stage':'producer bundle','coating':name,'bundle_sha256':sha(blob),
                                 'path':str((snaps/f'{name}_primary_feedback_{sha(blob)[:16]}.json').relative_to(ROOT))})
    base=(C/'index.json').read_bytes()
    if sha(base)!=DECISIONS[-1][2]:sys.exit('index.json is not the summary-time index')
    index=json.loads(base);rows={r['run_id']:r for r in index['runs']}
    selected={}
    for cid,f in (('mp-aaacjmqp','LiTaF6'),('mp-aaaaajby','LiCaAlF6')):
        b=json.loads((C/f'feedback/{f}_primary_feedback.json').read_text());selected[cid]={c:b['contacts'][c]['selected'] for c in b['contacts']}
    added=[]
    # Selected coatings: declared sensitivity rows.
    for cid,(folder,prefix) in ROBUSTNESS.items():
        jobs=jobs_from(C/f'robustness/{folder}/sacct.txt',prefix)
        for contact in ('cathode','electrolyte'):
            for short,slot in SLOTS.items():
                row=rows[f'{cid}:{contact}:sensitivity:{slot}'];run=C/f'robustness/{folder}/{contact}_{short}'
                if row['status'].startswith('not_run'):
                    row.update(quantified=False,note='declared unavailable before any energy for this coating; sensitivity unquantified');continue
                row.update(measured(run,selected[cid][contact]),quantified=True,job_id=jobs.get(f'{contact}_{short}',{}).get('job_id'),
                           released_after='summary (c0a0546)')
    # Unselected option: planned rows were never run.
    for r in index['runs']:
        if r['candidate_id']=='mp-aaaaabru':r.update(status='not_run_not_selected',quantified=False)
    # LiNbF6 reference: geometry-rule consistency runs and the archived seed-4 (Nb) sensitivity.
    ref_primary={'cathode':{'W_adh_J_m2':3.6170508624496,'W_sep_J_m2':5.167624545488891},
                 'electrolyte':{'W_adh_J_m2':1.6333940812860246,'W_sep_J_m2':2.9672197308623063}}
    jobs=jobs_from(C/'robustness/reference_consistency_v1/sacct.txt','refc')
    for contact in ('cathode','electrolyte'):
        for g in ('G2','G3'):
            row={'run_id':f'mp-aaacjjwh:{contact}:consistency:{g}','candidate_id':'mp-aaacjjwh','contact':contact,'role':'consistency',
                 'registry_id':g,'job_id':jobs.get(f'{contact}_{g}',{}).get('job_id'),'reused_from':None,'quantified':True}
            row.update(measured(C/f'robustness/reference_consistency_v1/{contact}_{g}',ref_primary[contact]));index['runs'].append(row);added.append(row['run_id'])
    row={'run_id':'mp-aaacjjwh:electrolyte:sensitivity:robustness_case','candidate_id':'mp-aaacjjwh','contact':'electrolyte','role':'sensitivity',
         'sensitivity_kind':'robustness_case','reused_from':'data/petmad/niflheim_batch1/electrolyte_seed4','quantified':True,
         'note':'archived seed-4 (Nb) run, registry (0,0), mapped Cl cut; same construction sensitivity as the Ta case'}
    row.update(measured(ROOT/'data/petmad/niflheim_batch1/electrolyte_seed4',ref_primary['electrolyte']));index['runs'].append(row);added.append(row['run_id'])
    # Accounting of new full jobs in this campaign (each: joined/film/substrate relaxations + 2 rigid single points).
    new=[r for r in index['runs'] if r['status']=='valid' and not r.get('reused_from')]
    groups={'primary (selected coatings)':[r for r in new if r['role']=='primary'],
            'sensitivity (selected coatings)':[r for r in new if r['role']=='sensitivity'],
            'consistency (LiNbF6 reference)':[r for r in new if r['role']=='consistency']}
    accounting={k:{'jobs':len(v),'calculator_calls':sum(r['calculator_calls'] for r in v),
                   'separation_single_points':sum(r.get('separation_single_points',0) for r in v),
                   'runner_wall_seconds':round(sum(r['wall_seconds'] for r in v),1)} for k,v in groups.items()}
    total=sum(a['jobs'] for a in accounting.values())
    accounting['total']={'jobs':total,'ceiling':36,'calculator_calls':sum(a['calculator_calls'] for a in accounting.values()),
                         'separation_single_points':sum(a['separation_single_points'] for a in accounting.values()),
                         'runner_wall_seconds':round(sum(a['runner_wall_seconds'] for a in accounting.values()),1),
                         'device':'RTX 3090 (sm3090el9_devel)','excludes':'bulk preparation (LiF/LiTaF6: 389 CPU calls), queue/setup time, '
                                  'and the five reused LiNbF6 reference primaries'}
    index.update(schema_version='coating_comparison_v1_final_robustness',derived_from_index_sha256=DECISIONS[-1][2],
                 decision_snapshots=snapshot_records,released_after_summary='origin/work/agent-experiments c0a0546',
                 job_accounting=accounting,
                 note='Primary rows and selections are identical to the decision-time indices. Sensitivity, consistency '
                      'and archived reference rows were released only after the final live call and never entered a decision.')
    index.pop('last_bundle',None)
    text=json.dumps(index,indent=1)+'\n';(C/'index_final.json').write_text(text)
    print(f"index_final sha256 {sha(text.encode())}; added {len(added)} rows; jobs {total} "
          f"({', '.join(f'{k}: {v['jobs']}' for k,v in accounting.items() if k!='total')})")

if __name__=='__main__':main()
