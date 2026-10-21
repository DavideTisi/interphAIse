#!/usr/bin/env python3
"""Download all required corrected entries, resume cached batches, pin endpoints."""
import argparse
from datetime import datetime, timezone
from importlib.metadata import version
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from dotenv import load_dotenv
from monty.json import MontyEncoder
from interphaise.tools.thermo_dataset import THERMO_TYPE, digest, required_systems, verify_hash, serialize_entry


def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data,cls=MontyEncoder,sort_keys=True,allow_nan=False))
    temp.replace(path)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pool',type=Path,default=ROOT/'data/pools/mp_candidates_v2.json')
    ap.add_argument('--cache',type=Path,default=ROOT/'runs/thermo_v2')
    ap.add_argument('--output',type=Path,default=ROOT/'runs/thermo_v2/dataset.json')
    args=ap.parse_args()
    if args.output.exists():
        ap.error('Output exists; use its cached data or choose a new versioned path')
    pool=json.loads(args.pool.read_text()); verify_hash(pool)
    load_dotenv(ROOT/'.env')
    key=os.environ.get('MY_MP_API_KEY','').strip()
    if not key:
        ap.error('MY_MP_API_KEY missing')
    from mp_api.client import MPRester
    try:
        with MPRester(key,mute_progress_bars=True) as m:
            db_version=m.db_version
            endpoint_path=args.cache/'endpoints.json'
            if endpoint_path.exists():
                endpoints=json.loads(endpoint_path.read_text())
                if endpoints['db_version']!=db_version:
                    raise ValueError('Database changed; use a new cache directory')
            else:
                docs=m.materials.summary.search(formula=['LiCoO2','Li6PS5Cl'],
                    fields=['material_id','formula_pretty','structure','energy_above_hull','origins'])
                selected={}
                for role,formula in [('electrode','LiCoO2'),('electrolyte','Li6PS5Cl')]:
                    eligible=[d for d in docs if d.formula_pretty==formula and d.structure.is_ordered
                              and d.energy_above_hull is not None]
                    d=min(eligible,key=lambda d:(d.energy_above_hull,str(d.material_id)))
                    selected[role]=d.model_dump(mode='json')
                endpoints={'db_version':db_version,'selection':'lowest summary hull ordered polymorph per formula',
                           'voltage_V':4.0,**selected}
                write_json(endpoint_path,endpoints)
            systems=required_systems(pool,'LiCoO2','Li6PS5Cl')
            all_entries={}; batches=[]
            for start in range(0,len(systems),40):
                query=systems[start:start+40]
                path=args.cache/('batch-'+digest(query)[:16]+'.json')
                if path.exists():
                    batch=json.loads(path.read_text())
                    verify_hash(batch)
                    if batch['db_version']!=db_version or batch['thermo_type']!=THERMO_TYPE or batch['systems']!=query:
                        raise ValueError('Cache provenance mismatch')
                else:
                    entries=m.get_entries(query,compatible_only=True,
                        additional_criteria={'thermo_types':[THERMO_TYPE]},
                        property_data=['material_id','thermo_type'])
                    serialized=[serialize_entry(e) for e in entries]
                    batch={'db_version':db_version,'thermo_type':THERMO_TYPE,'systems':query,
                           'retrieved_at':datetime.now(timezone.utc).isoformat(),
                           'entries':sorted(serialized,key=lambda e:str(e['entry_id']))}
                    batch['sha256']=digest(batch); write_json(path,batch)
                for entry in batch['entries']:
                    eid=str(entry['entry_id'])
                    if eid in all_entries and all_entries[eid]!=entry:
                        raise ValueError('Conflicting corrected entries')
                    all_entries[eid]=entry
                batches.append({'systems':query,'sha256':batch['sha256'],'entry_count':len(batch['entries'])})
                print(f'Subsystems {min(start+40,len(systems))}/{len(systems)}; entries {len(all_entries)}',flush=True)
            dataset={'schema_version':'thermo-dataset-v2','thermo_type':THERMO_TYPE,
                     'db_version':db_version,'mp_api_version':version('mp-api'),
                     'pool_sha256':pool['sha256'],'endpoints':endpoints,'batches':batches,
                     'created_at':datetime.now(timezone.utc).isoformat(),
                     'entries':[all_entries[k] for k in sorted(all_entries)]}
            dataset['sha256']=digest(dataset); write_json(args.output,dataset)
            print(json.dumps({'dataset':str(args.output),'sha256':dataset['sha256'],'entries':len(all_entries)}))
    except Exception as exc:
        import traceback
        frames = traceback.extract_tb(exc.__traceback__)
        print(f'Dataset retrieval failed ({type(exc).__name__}); completed batches retained.',file=sys.stderr)
        print('Failure locations: '+ ' > '.join(f'{Path(f.filename).name}:{f.lineno}' for f in frames),file=sys.stderr)
        return 1
    return 0

if __name__=='__main__':
    raise SystemExit(main())
