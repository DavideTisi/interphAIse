#!/usr/bin/env python3
"""Freeze a scientifically reviewed draft without changing numerical outcomes."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from interphaise.tools.thermo_dataset import digest,verify_hash


def freeze(source,version,decision):
    verify_hash(source)
    if source['status']!='draft-requires-scientific-review':
        raise ValueError('Expected an unfrozen diagnostic benchmark')
    if not version or 'draft' in version or not decision.strip():
        raise ValueError('A final version and scientific decision record are required')
    original=source['objective']
    if source['objective_sha256']!=digest(original):
        raise ValueError('Objective hash mismatch')
    result=deepcopy(source)
    result['status']='frozen'
    result['frozen_from_sha256']=source['sha256']
    result['freeze_decision']=decision
    result['frozen_at']=datetime.now(timezone.utc).isoformat()
    result['objective']['version']=version
    result['objective_sha256']=digest(result['objective'])
    for row in result['results']:
        if row['status']=='ok' and row.get('objective')!=original:
            raise ValueError('Mixed objectives in source benchmark')
        row['objective']=deepcopy(result['objective'])
        row['objective_version']=version
    del result['sha256']
    result['sha256']=digest(result)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--version',required=True)
    ap.add_argument('--decision',required=True)
    args=ap.parse_args()
    if args.output.exists():ap.error('Never overwrite a frozen benchmark; use a new version')
    result=freeze(json.loads(args.input.read_text()),args.version,args.decision)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n')
    print(json.dumps({'output':str(args.output),'sha256':result['sha256'],
                      'objective_sha256':result['objective_sha256']}))

if __name__=='__main__':main()
