#!/usr/bin/env python3
"""Fetch a complete, resumable, version-consistent expansion dataset (no LLMs)."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import gzip
from importlib.metadata import version
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from interphaise.tools.thermo_dataset import (
    THERMO_TYPE, digest, load_entries, required_systems, serialize_entry, verify_hash,
)


def write_hashed(path, data):
    """Atomic sanitized JSON; deterministic gzip header, semantic content hash."""
    path = Path(path)
    data = {k: v for k, v in data.items() if k != 'sha256'}
    data['sha256'] = digest(data)
    payload = (json.dumps(data, sort_keys=True, allow_nan=False) + '\n').encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_bytes(gzip.compress(payload, mtime=0) if path.suffix == '.gz' else payload)
    temp.replace(path)
    return data


def all_required_systems(pool, plan):
    return sorted({s for env in plan['environments'] for s in required_systems(
        pool, env['endpoints']['electrode']['formula'], env['endpoints']['electrolyte']['formula'])})


def source_for_version(source, db_version):
    """Never combine database vintages or correction schemes."""
    if source['db_version'] == db_version and source['thermo_type'] == THERMO_TYPE:
        return source
    return None


def merge_entries(target, incoming):
    for entry in incoming:
        if entry.get('data', {}).get('thermo_type') != THERMO_TYPE:
            raise ValueError('Unexpected entry correction scheme')
        if entry.get('data', {}).get('run_type') not in {'GGA', 'GGA_U', 'GGA+U'}:
            raise ValueError('Unexpected entry functional')
        eid = str(entry['entry_id'])
        if eid in target and target[eid] != entry:
            raise ValueError(f'Conflicting duplicate entry {eid}')
        target[eid] = entry


def validate_coverage(pool, plan, dataset):
    required = set(all_required_systems(pool, plan))
    covered = {s for batch in dataset['batches'] for s in batch['systems']}
    missing = sorted(required - covered)
    if missing:
        raise ValueError(f'Incomplete competing-phase coverage: {len(missing)} systems')
    if dataset['pool_sha256'] != pool['sha256'] or dataset['plan_sha256'] != plan['sha256']:
        raise ValueError('Expansion pool/plan provenance mismatch')
    return len(required)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pool', type=Path, default=ROOT/'data/exploration/environment_expansion_v1/pool.json')
    ap.add_argument('--plan', type=Path, default=ROOT/'data/exploration/environment_expansion_v1/plan.json')
    ap.add_argument('--source', type=Path, default=ROOT/'data/thermo/mp_gga_v2.json.gz')
    ap.add_argument('--cache', type=Path, default=ROOT/'runs/environment_expansion_v2/fetch')
    ap.add_argument('--output', type=Path, default=ROOT/'data/exploration/environment_expansion_v2/dataset.json.gz')
    ap.add_argument('--batch-size', type=int, default=40)
    args = ap.parse_args()
    if args.output.exists():
        ap.error('Output exists; choose a fresh versioned path')
    if not 1 <= args.batch_size <= 40:
        ap.error('Batch size must be between 1 and 40')
    pool = json.loads(args.pool.read_text()); verify_hash(pool)
    plan = json.loads(args.plan.read_text()); verify_hash(plan)
    if plan['pool_sha256'] != pool['sha256']:
        ap.error('Pool/plan mismatch')
    source, _ = load_entries(args.source)
    if source['sha256'] != plan['existing_dataset_sha256']:
        ap.error('Unexpected source dataset')
    from dotenv import load_dotenv
    load_dotenv(ROOT/'.env')
    key = os.environ.get('MY_MP_API_KEY', '').strip()
    if not key:
        ap.error('MY_MP_API_KEY missing from local ignored environment')
    started = datetime.now(timezone.utc).isoformat()
    try:
        from mp_api.client import MPRester
        with MPRester(key, mute_progress_bars=True) as m:
            db_version = m.db_version
            reusable = source_for_version(source, db_version)
            all_entries = {}; batches = []
            if reusable:
                merge_entries(all_entries, reusable['entries'])
                batches = [{**b, 'source_dataset_sha256': source['sha256']} for b in source['batches']]
            required = all_required_systems(pool, plan)
            covered = {s for b in batches for s in b['systems']}
            missing = sorted(set(required) - covered)
            print(json.dumps({'db_version': db_version, 'reuse_source': bool(reusable),
                              'required_systems': len(required), 'new_systems': len(missing)}), flush=True)
            cache_manifest = {'db_version': db_version, 'thermo_type': THERMO_TYPE,
                              'pool_sha256': pool['sha256'], 'plan_sha256': plan['sha256'],
                              'source_reused': source['sha256'] if reusable else None,
                              'batch_size': args.batch_size, 'new_systems_sha256': digest(missing)}
            manifest_path = args.cache/'manifest.json'
            if manifest_path.exists():
                previous = json.loads(manifest_path.read_text()); verify_hash(previous)
                if {k:v for k,v in previous.items() if k != 'sha256'} != cache_manifest:
                    raise ValueError('Cache provenance changed; use a new cache directory')
            else:
                write_hashed(manifest_path, cache_manifest)
            requests = 0; cached_batches = 0
            for start in range(0, len(missing), args.batch_size):
                query = missing[start:start+args.batch_size]
                path = args.cache/('batch-' + digest(query)[:16] + '.json')
                if path.exists():
                    batch = json.loads(path.read_text()); verify_hash(batch)
                    if (batch['db_version'] != db_version or batch['thermo_type'] != THERMO_TYPE
                            or batch['systems'] != query):
                        raise ValueError('Cached batch provenance mismatch')
                    cached_batches += 1
                else:
                    entries = m.get_entries(query, compatible_only=True,
                        additional_criteria={'thermo_types': [THERMO_TYPE]},
                        property_data=['material_id', 'thermo_type'])
                    requests += 1
                    batch = write_hashed(path, {
                        'db_version': db_version, 'thermo_type': THERMO_TYPE, 'systems': query,
                        'retrieved_at': datetime.now(timezone.utc).isoformat(),
                        'entries': sorted((serialize_entry(e) for e in entries), key=lambda e: str(e['entry_id']))})
                merge_entries(all_entries, batch['entries'])
                batches.append({k:batch[k] for k in ('systems', 'sha256', 'retrieved_at')})
                batches[-1]['entry_count'] = len(batch['entries'])
                print(f"New systems {min(start+args.batch_size,len(missing))}/{len(missing)}; entries {len(all_entries)}", flush=True)
            # MPRester.get_database_version() merely returns the cached attribute.
            # This public, credential-free heartbeat must actually be fetched again.
            import requests as http
            heartbeat = http.get(m.endpoint.rstrip('/') + '/heartbeat', timeout=30)
            heartbeat.raise_for_status()
            final_version = heartbeat.json()['db_version']
            if final_version != db_version:
                raise ValueError('Database version changed during retrieval')
            dataset = {
                'schema_version': 'environment-thermo-dataset-v1',
                'status': 'complete-queries-exploratory-not-frozen',
                'thermo_type': THERMO_TYPE, 'db_version': db_version,
                'db_version_verified_after_fetch': final_version,
                'mp_api_version': version('mp-api'), 'pool_sha256': pool['sha256'],
                'plan_sha256': plan['sha256'], 'environments': plan['environments'],
                'source_dataset_sha256': source['sha256'] if reusable else None,
                'source_dataset_reused': bool(reusable), 'started_at': started,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'accounting': {'new_get_entries_calls_this_invocation': requests,
                               'resumed_cached_batches': cached_batches,
                               'additional_batch_count': requests + cached_batches,
                               'additional_system_count': len(missing),
                               'required_system_count': len(required),
                               'llm_calls': 0, 'mlip_calls': 0},
                'batches': batches, 'entries': [all_entries[k] for k in sorted(all_entries)],
            }
            validate_coverage(pool, plan, dataset)
            dataset = write_hashed(args.output, dataset)
            print(json.dumps({'output': str(args.output), 'sha256': dataset['sha256'],
                              'entry_count': len(all_entries)}), flush=True)
    except Exception as exc:
        # API exception strings can contain requests; never print them or headers.
        import traceback
        locations = ' > '.join(f'{Path(f.filename).name}:{f.lineno}'
                               for f in traceback.extract_tb(exc.__traceback__))
        print(f'Retrieval failed ({type(exc).__name__}); cached batches retained. Locations: {locations}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
