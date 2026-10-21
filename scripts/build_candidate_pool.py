#!/usr/bin/env python3
"""Build a reproducible draft MP pool; never selects using benchmark outcomes.

Uses the official summary REST endpoint, caches raw responses outside tracked
files, and supports offline replay. Summary hull energies are ONLY prefilters;
benchmark energies must later come from a consistent corrected thermo dataset.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import random
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from pymatgen.core import Structure

ROOT = Path(__file__).resolve().parents[1]
FIELDS = 'material_id,formula_pretty,structure,band_gap,energy_above_hull,origins,last_updated'
# Restricted chemistry keeps phase diagrams and the two-day study manageable.
ALLOWED = {'Li','O','P','B','Si','Al','Mg','Ca','Zn','Ti','Zr','Nb','Ta','F','Cl','Br','I'}


def fetch_documents(cache: Path, offline: bool):
    if cache.exists():
        return json.loads(cache.read_text())
    if offline:
        raise ValueError('Offline snapshot missing')
    load_dotenv(ROOT / '.env')
    key = os.environ.get('MY_MP_API_KEY','').strip()
    if not key:
        raise ValueError('MY_MP_API_KEY is missing')
    responses = []
    docs = {}
    for anion in ['O','F','Cl','Br','I']:
        skip = 0
        while True:
            params = {'elements':f'Li,{anion}', 'energy_above_hull_max':0.025,
                      'deprecated':'false', '_fields':FIELDS, '_limit':500, '_skip':skip}
            request = Request('https://api.materialsproject.org/materials/summary/?' + urlencode(params),
                              headers={'X-API-KEY':key,'User-Agent':'interphaise-pool/2.0'})
            with urlopen(request, timeout=90) as response:
                payload = json.load(response)
            batch = payload['data']
            responses.append({'query':params,'meta':payload.get('meta',{})})
            for doc in batch:
                docs[doc['material_id']] = doc
            skip += len(batch)
            total = payload.get('meta',{}).get('total_doc')
            if not batch or (total is not None and skip >= total) or len(batch)<500:
                break
            if skip >= 10000:
                raise ValueError('Query exceeded safety cap; narrow filters explicitly')
    snapshot = {'retrieved_at':datetime.now(timezone.utc).isoformat(),
                'requests':responses,'documents':list(docs.values())}
    cache.parent.mkdir(parents=True,exist_ok=True)
    cache.write_text(json.dumps(snapshot,sort_keys=True))
    return snapshot


def family(elements):
    if {'P','O'} <= elements:
        return 'phosphate'
    if {'B','O'} <= elements:
        return 'borate'
    if {'Si','O'} <= elements:
        return 'silicate'
    if 'O' in elements:
        return 'other_oxide'
    return 'halide'


def select_pool(snapshot, size=50, seed=2026):
    groups = defaultdict(list)
    rejected = []
    for doc in sorted(snapshot['documents'],key=lambda d:d['material_id']):
        reason = None
        structure = Structure.from_dict(doc['structure'])
        elements = {str(e) for e in structure.composition.elements}
        hull = doc.get('energy_above_hull')
        if 'Li' not in elements or not elements <= ALLOWED or len(elements)>4:
            reason = 'chemical_scope'
        elif hull is None or not math.isfinite(hull) or hull < -1e-8 or hull>0.025:
            reason = 'hull_prefilter'
        elif not structure.is_ordered:
            reason = 'disordered'
        if reason is None:
            primitive = structure.get_primitive_structure()
            if len(primitive)>40:
                reason = 'primitive_cell_too_large'
        if reason:
            rejected.append({'material_id':doc['material_id'],'reason':reason})
            continue
        kind = family(elements)
        gap = doc.get('band_gap')
        groups[kind].append({
            'candidate_id':doc['material_id'], 'material_id':doc['material_id'],
            'formula':doc['formula_pretty'], 'family':kind,
            'band_gap_eV':gap if gap is not None and math.isfinite(gap) else None,
            'summary_energy_above_hull_eV_atom':hull,
            'primitive_nsites':len(primitive), 'structure':primitive.as_dict(),
            'origins':doc.get('origins',[]),'last_updated':doc.get('last_updated'),
        })
    rng = random.Random(seed)
    for kind in sorted(groups):
        rng.shuffle(groups[kind])
    selected = []
    while len(selected)<size and any(groups.values()):
        for kind in sorted(groups):
            if groups[kind] and len(selected)<size:
                selected.append(groups[kind].pop())
    if len(selected)<size:
        raise ValueError(f'Only {len(selected)} eligible candidates; requested {size}')
    selected.sort(key=lambda d:d['candidate_id'])
    body = {
        'schema_version':'candidate-pool-v2', 'status':'draft-not-benchmark-frozen',
        'seed':seed, 'source':'Materials Project summary REST API',
        'retrieved_at':snapshot['retrieved_at'], 'requests':snapshot['requests'],
        'filters':{'max_summary_hull_eV_atom':0.025,'ordered':True,'max_primitive_sites':40,
                   'max_elements':4,'allowed_elements':sorted(ALLOWED),
                   'band_gap_filter':None,'selection':'seeded family round-robin; polymorphs retained'},
        'counts':{'downloaded':len(snapshot['documents']),'selected':len(selected),
                  'families':dict(Counter(c['family'] for c in selected)),
                  'eligible_unselected':sum(map(len,groups.values()))},
        'rejected':rejected, 'candidates':selected,
        'limitations':['Summary energies are prefilters, not a compatible phase-diagram dataset.',
                       'Material IDs align summary structure and gap; origins record separate property calculations.',
                       'No Li-transport or synthesis criterion. Gap is not used to preselect the pool.'],
    }
    body['sha256'] = hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    return body


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--size',type=int,default=50)
    parser.add_argument('--seed',type=int,default=2026)
    parser.add_argument('--cache',type=Path,default=ROOT/'runs/mp_pool_snapshot.json')
    parser.add_argument('--output',type=Path,default=ROOT/'data/pools/mp_candidates_v2.json')
    parser.add_argument('--offline',action='store_true')
    args = parser.parse_args()
    if args.size<1:
        parser.error('--size must be positive')
    if args.output.exists():
        parser.error('Output already exists; use a new versioned path')
    try:
        pool = select_pool(fetch_documents(args.cache,args.offline),args.size,args.seed)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(pool,indent=2,sort_keys=True,allow_nan=False)+'\n')
    except Exception as error:
        # Never print raw network exceptions/headers in credentialed workflows.
        print(f'Pool build failed ({type(error).__name__}); no pool written.',file=sys.stderr)
        return 1
    print(json.dumps({'output':str(args.output),'sha256':pool['sha256'],'counts':pool['counts']}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
