#!/usr/bin/env python3
"""Exhaustive draft validation; no LLM calls and no automatic experiment freeze."""
import argparse
from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import version
import json
import math
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from pymatgen.core import Composition, Structure
from interphaise.discovery_evaluator import Objective, evaluate_candidate, ranking_key
from interphaise.tools.thermo_dataset import digest, load_entries, resolve_entry, verify_hash


def diagnostics(results):
    valid=[r for r in results if r['status']=='ok' and r.get('insulating')]
    optimum=max((ranking_key(r) for r in valid),default=None)
    best=[r['candidate_id'] for r in valid if ranking_key(r)==optimum]
    floors=[r for r in valid if abs(r['penalty']-max(r['endpoint_decomposition_penalties'].values()))<1e-7]
    n=len(results); m=len(best)
    random_curve=[{'evaluations':k,'probability_find_best_bin':
                   1-(math.comb(n-m,k)/math.comb(n,k) if k<=n-m else 0)} for k in range(n+1)]
    acceptable=sum(r.get('acceptable',False) for r in results)
    blockers=[]
    if len(valid)!=n:
        blockers.append('Some candidates failed calculation or insulation; retain them in budget accounting')
    if not acceptable:
        blockers.append('No candidate meets the proposed absolute acceptability threshold')
    if len(best)>n/2:
        blockers.append('More than half the pool ties in the best eligible bin; search discrimination is weak')
    if floors:
        blockers.append('Endpoint self-decomposition sets the worst penalty for some eligible candidates')
    return {'total':n,'status_counts':dict(Counter(r['status'] for r in results)),
            'eligible':len(valid),'acceptable':acceptable,
            'eligible_bin_counts':dict(sorted(Counter(r['penalty_bin'] for r in valid).items())),
            'best_candidate_ids':best,'best_bin':-optimum[1] if optimum else None,
            'endpoint_floor_count':len(floors),'random_best_bin_success':random_curve,
            'review_findings':blockers}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pool',type=Path,default=ROOT/'data/pools/mp_candidates_v2.json')
    ap.add_argument('--dataset',type=Path,default=ROOT/'data/thermo/mp_gga_v2.json.gz')
    ap.add_argument('--contact-reference',choices=['pinned','equilibrated'],default='pinned')
    ap.add_argument('--output',type=Path,default=ROOT/'runs/benchmark_v2_draft.json')
    args=ap.parse_args()
    if args.output.exists(): ap.error('Output exists; choose a new versioned path')
    pool=json.loads(args.pool.read_text());verify_hash(pool)
    dataset,entries=load_entries(args.dataset)
    if dataset['pool_sha256']!=pool['sha256']: ap.error('Dataset/pool hash mismatch')
    endpoints=dataset['endpoints']
    pinned={role:resolve_entry(entries,endpoints[role]['material_id'],Structure.from_dict(endpoints[role]['structure']))
            for role in ('electrode','electrolyte')}
    results=[]
    objective=Objective() if args.contact_reference=='pinned' else Objective(
        version='v3-draft',contact_reference='equilibrated')
    for candidate in pool['candidates']:
        started=time.monotonic()
        try:
            coating=resolve_entry(entries,candidate['material_id'],Structure.from_dict(candidate['structure']))
            allowed={e for entry in [coating,*pinned.values()] for e in entry.composition.elements}
            subset=[e for e in entries if set(e.composition.elements)<=allowed]
            result=evaluate_candidate(candidate['candidate_id'],coating,
                electrode_entry=pinned['electrode'],electrolyte_entry=pinned['electrolyte'],
                entries=subset,voltage=endpoints['voltage_V'],band_gap_eV=candidate['band_gap_eV'],
                energy_source=f"MP {dataset['db_version']} {dataset['thermo_type']}; dataset {dataset['sha256']}",
                objective=objective)
            result['thermo_entry_count']=len(subset)
        except Exception as exc:
            # Offline errors contain no request credentials. Keep known validation messages only.
            result={'candidate_id':candidate['candidate_id'],'status':'failed',
                    'error_type':type(exc).__name__,
                    'error':str(exc) if isinstance(exc,ValueError) else 'Unexpected offline evaluation failure'}
        result['formula']=candidate['formula']
        result['evaluation_wall_seconds']=time.monotonic()-started
        results.append(result)
        print(f"{len(results)}/{len(pool['candidates'])} {candidate['formula']}: {result['status']}",flush=True)
    from dataclasses import asdict
    body={'schema_version':'coating-benchmark-v2','status':'draft-requires-scientific-review',
          'pool_sha256':pool['sha256'],'dataset_sha256':dataset['sha256'],
          'objective':asdict(objective),'objective_sha256':digest(asdict(objective)),
          'endpoints':{r:{'material_id':str(endpoints[r]['material_id']),
                         'formula':endpoints[r]['formula_pretty']} for r in pinned},
          'voltage_V':endpoints['voltage_V'],'created_at':datetime.now(timezone.utc).isoformat(),
          'versions':{p:version(p) for p in ('pymatgen','pymatgen-core','scipy','mp-api')},
          'diagnostics':diagnostics(results),'results':results}
    body['sha256']=digest(body)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(body,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps(body['diagnostics'],indent=2))

if __name__=='__main__':main()
