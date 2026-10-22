import json, pathlib, hashlib, math, subprocess
# Run from the repository root. Reads immutable Git objects, never live APIs.
root=pathlib.Path.cwd(); src=root/'presentations/.build/results_synthesis/sources'
src.mkdir(parents=True,exist_ok=True)
AGENT='800ba0378779ce7df9038bc4857719a29c2fe0a7'
PHYSICS='1b76eeb0330ae1ddee3720d76145c2b308725245'
DAVIDE='750b382844fd64aaa46f96ce96be1871e992c0f1'
inputs={
 'environment.json':(AGENT,'data/experiments/environment_v1/environment_summary.json'),
 'original.json':(DAVIDE,'data/experiments/integrated_v3_20261021_s100/summary.json'),
 'shuffled.json':(AGENT,'data/experiments/shuffled_v3_20261021_s100/summary.json'),
 'pilot_final.json':(PHYSICS,'data/petmad/coating_comparison_v1/index_final.json'),
}
for name,(ref,file) in inputs.items():
 (src/name).write_bytes(subprocess.check_output(['git','show',f'{ref}:{file}']))
def read(n): return json.loads((src/n).read_text())
e=read('environment.json'); original=read('original.json'); shuffle=read('shuffled.json'); idx=read('pilot_final.json')
order=['iterative','sequential','shuffled','upfront','random']
envs=['Li6PS5Cl','Li3InCl6','Li7La3Zr2O12']; M=[4,55,17]
out={'title':'interphAIse results synthesis, 22 October 2026','sources':{'davide_commit':DAVIDE,'agent_commit':AGENT,'physics_commit':PHYSICS,'final_index_sha256':hashlib.sha256((src/'pilot_final.json').read_bytes()).hexdigest()},'arm_order':order,'environment_order':envs,'environments':{},'original':{},'physical':{}}
assert out['sources']['final_index_sha256']=='47d69f7dd75dff89e1d2e5191f2f1d31fad002581521c39eeee7593c90d83c41'
for env,m in zip(envs,M):
 d=e['environments'][env]; row={'pool_size':141,'acceptable_candidates':m,'counts':{},'curves':{},'contrasts':d['contrasts'],'hashes':d['hashes'],'best_bin':{},'first_hit_counts':{}}
 for arm in order:
  a=d['arms'][arm]; assert a['runs']==30
  row['counts'][arm]=a['acceptable'];row['best_bin'][arm]=a['best_bin_found'];row['first_hit_counts'][arm]=a['first_acceptable_counts']
  row['curves'][arm]=[sum(a['first_acceptable_counts'].get(str(j),0) for j in range(1,k+1))/30 for k in range(1,11)]
  assert round(row['curves'][arm][-1]*30)==row['counts'][arm]
 row['random_exact_curve']=[1-math.comb(141-m,k)/math.comb(141,k) for k in range(1,11)]
 out['environments'][env]=row
assert [out['environments'][envs[0]]['counts'][a] for a in order]==[20,2,6,0,8]
assert [out['environments'][envs[1]]['counts'][a] for a in order]==[30,30,30,30,29]
assert [out['environments'][envs[2]]['counts'][a] for a in order]==[12,0,4,1,24]
for arm in order:
 d=(shuffle if arm=='shuffled' else original)['curves']['acceptable'][arm]
 out['original'][arm]={'count':round(d[0][-1]*30),'curve':d[0]}
assert [out['original'][a]['count'] for a in order]==[19,4,6,4,10]
out['original']['random_exact_curve']=shuffle['curves']['acceptable']['random (exact)'][0]
for menu in idx['menu']:
 cid=menu['candidate_id'];f=menu['formula']
 if f not in ['LiNbF6','LiTaF6','LiCaAlF6']: continue
 row={'candidate_id':cid,'contacts':{}}
 for contact in ['cathode','electrolyte']:
  runs=[r for r in idx['runs'] if r['candidate_id']==cid and r['contact']==contact and r['role']=='primary' and r['status']=='valid']
  best=min(runs,key=lambda x:x['joined_energy_eV'])
  row['contacts'][contact]={k:best[k] for k in ['W_adh_J_m2','W_sep_J_m2','registry_id','registry','n_atoms','result_path','joined_energy_eV']}
  row['contacts'][contact]['registry_range']=[min(r['W_adh_J_m2'] for r in runs),max(r['W_adh_J_m2'] for r in runs)]
 out['physical'][f]=row
out['forecast']=[{'coating':f,'contact':c,'range':ran,'observed':out['physical'][f]['contacts'][c]['W_adh_J_m2']} for f,c,ran in [('LiTaF6','cathode',[3.2,3.9]),('LiTaF6','electrolyte',[1.4,1.9]),('LiCaAlF6','cathode',[3.0,3.8]),('LiCaAlF6','electrolyte',[1.4,1.9])]]
out['job_accounting']=idx['job_accounting']
audit=json.loads(subprocess.check_output(['git','show',DAVIDE+':data/reviews/llzo_chemistry_audit_20261021.json']));out['llzo_audit']={a:{k:v[k] for k in ['distinct_formulas','acceptable_picks','successful_runs','unflagged_hit_runs','acceptable_picks_by_query_index']} for a,v in audit['arms'].items()}
out['source_file_sha256']={f:hashlib.sha256((src/f).read_bytes()).hexdigest() for f in ['environment.json','original.json','shuffled.json','pilot_final.json']}
(root/'presentations/source/results_synthesis_2026-10-22.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'sources':out['sources'],'physical':out['physical'],'counts':{n:v['counts'] for n,v in out['environments'].items()}},indent=2))
