#!/usr/bin/env python3
"""Freeze copies of all reviewed environment tables, preserving every scientific value.

This freezes data, not spending approval or the experiment protocol. Draft inputs
are retained so their original hashes and offline checks remain reproducible.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from interphaise.tools.thermo_dataset import digest, verify_hash

ENVIRONMENTS = ('lco_lpscl_4v', 'lco_lic_4v', 'lco_llzo_4v')


def freeze_tables(pool, sources, *, decision, frozen_at):
    """Validate the complete set before returning new objects; never mutate inputs."""
    verify_hash(pool)
    if not decision.strip() or not frozen_at:
        raise ValueError('A scientific decision and timestamp are required')
    ids = [c['candidate_id'] for c in pool['candidates']]
    if len(set(ids)) != len(ids):
        raise ValueError('Duplicate pool IDs')
    if len(sources) != 3 or {s['environment_id'] for s in sources} != set(ENVIRONMENTS):
        raise ValueError('Freeze exactly the three declared environments together')
    common = ('objective_sha256', 'dataset_sha256', 'plan_sha256', 'voltage_V')
    frozen = []
    for source in sources:
        verify_hash(source)
        if source['status'] != 'exploratory-exhaustive-not-frozen':
            raise ValueError('Expected an unfrozen environment table')
        if source['pool_sha256'] != pool['sha256']:
            raise ValueError('Pool/table mismatch')
        if source['objective_sha256'] != digest(source['objective']):
            raise ValueError('Objective hash mismatch')
        if any(source[k] != sources[0][k] for k in common):
            raise ValueError('Mixed scientific inputs across environments')
        row_ids = [r['candidate_id'] for r in source['results']]
        if len(row_ids) != len(ids) or set(row_ids) != set(ids):
            raise ValueError('Expected exactly one result per candidate')
        for row in source['results']:
            if row['status'] == 'ok' and row.get('objective') != source['objective']:
                raise ValueError('Mixed objectives within a table')
            if row['status'] not in ('ok', 'failed'):
                raise ValueError('Unexpected result status')
        result = deepcopy(source)
        result.update(status='frozen', frozen_from_sha256=source['sha256'],
                      frozen_at=frozen_at, freeze_decision=decision,
                      freeze_version='environment-data-v1')
        del result['sha256']
        result['sha256'] = digest(result)
        frozen.append(result)
    return frozen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pool', type=Path, default=ROOT/'data/exploration/environment_expansion_v1/pool.json')
    parser.add_argument('--source', type=Path, default=ROOT/'data/exploration/environment_expansion_v2/evaluation')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--decision', required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Never overwrite a frozen snapshot; choose a new directory')
    paths = [args.source/(env+'.json') for env in ENVIRONMENTS]
    sources = [json.loads(p.read_text()) for p in paths]
    pool = json.loads(args.pool.read_text())
    stamp = datetime.now(timezone.utc).isoformat()
    frozen = freeze_tables(pool, sources, decision=args.decision, frozen_at=stamp)
    args.output.mkdir(parents=True)
    files = {}
    for table in frozen:
        name = table['environment_id']+'.json'
        content = (json.dumps(table, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()
        (args.output/name).write_bytes(content)
        files[name] = {'sha256':table['sha256'], 'file_sha256':hashlib.sha256(content).hexdigest(),
                       'source_sha256':table['frozen_from_sha256']}
    manifest = {'schema_version':'frozen-environment-data-v1', 'created_at':stamp,
                'scope':'Data freeze only; no paid-run authorization',
                'pool_sha256':pool['sha256'], 'objective_sha256':sources[0]['objective_sha256'],
                'dataset_sha256':sources[0]['dataset_sha256'], 'decision':args.decision,
                'source_file_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                'freezer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'files':files}
    manifest['sha256'] = digest(manifest)
    (args.output/'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'output':str(args.output), 'manifest_sha256':manifest['sha256'], 'tables':files}, indent=2))


if __name__ == '__main__':
    main()
