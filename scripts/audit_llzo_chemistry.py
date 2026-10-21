#!/usr/bin/env python3
"""Post-hoc descriptive LLZO audit; never changes scores, eligibility or frozen inputs.

The three formulas below are an explicit oxyhalogen review set, not a validated
complete hazard classifier. LiIO3/LiClO4 have supplier oxidizer classifications;
Li5IO6 is a periodate family flag (compound-specific GHS classification unverified).
Each observed run retains all ten original queries. 'Unflagged-hit runs' partitions
existing outcomes, not a rerun on a filtered pool or a new primary endpoint.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re

from pymatgen.core import Composition
from pymatgen.entries.computed_entries import ComputedStructureEntry

from interphaise.tools.thermo_dataset import canonical_id, verify_hash

ROOT=Path(__file__).resolve().parents[1]
FLAGS={
    'LiIO3': {'name':'lithium iodate','evidence':'supplier oxidizing-solid classification',
              'source':'https://www.espimetals.com/msds/648-Lithium%20Iodate'},
    'LiClO4': {'name':'lithium perchlorate','evidence':'supplier oxidizing-solid classification',
               'source':'https://www.sigmaaldrich.com/US/en/product/aldrich/931969'},
    'Li5IO6': {'name':'lithium orthoperiodate','evidence':'I(VII) periodate identity; family-level practical-review flag, no compound-specific GHS classification verified',
               'source':'https://www.jstage.jst.go.jp/article/bunsekikagaku1952/26/3/26_3_191/_pdf'},
}
ARMS=('random','upfront','sequential','iterative','shuffled')
HAZARD_TERMS = re.compile(r'perchlor|iodate|periodate|oxidizer|oxidiser|hazard|explos', re.I)


def cached_perchlorate_reaction(table, candidate_id):
    """One diagnostic reaction using existing corrected entries, not a new score.

    Choose the pinned coating entry and the lowest energy per formula among
    cached LiCl and elemental oxygen entries. Mu_Li cancels for this reaction.
    This arithmetic cannot establish why the proxy differs from practical
    thermal behaviour or supply a finite-temperature free energy.
    """
    path = ROOT / 'data/exploration/environment_expansion_v2/dataset.json.gz'
    with gzip.open(path, 'rt') as stream:
        dataset = json.load(stream)
    verify_hash(dataset)
    assert dataset['sha256'] == table['dataset_sha256']
    pinned_id = canonical_id(candidate_id)
    buckets = {'LiClO4': [], 'LiCl': [], 'O2': []}
    for raw in dataset['entries']:
        composition = Composition(raw['composition'])
        formula, factor = composition.get_reduced_formula_and_factor()
        if formula not in buckets:
            continue
        if formula == 'LiClO4' and canonical_id(raw['data']['material_id']) != pinned_id:
            continue
        entry = ComputedStructureEntry.from_dict(raw)
        buckets[formula].append((entry.energy / factor, str(entry.entry_id)))
    selected = {}
    for formula, entries in buckets.items():
        energy, entry_id = min(entries)
        selected[formula] = {
            'entry_id': entry_id,
            'energy_per_formula_eV': energy,
            'available_entries': len(entries),
        }
    delta = (selected['LiCl']['energy_per_formula_eV']
             + 2 * selected['O2']['energy_per_formula_eV']
             - selected['LiClO4']['energy_per_formula_eV'])
    return {
        'dataset_sha256': dataset['sha256'],
        'dataset_file_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'reaction': 'LiClO4 -> LiCl + 2 O2',
        'entries': selected,
        'delta_energy_eV_per_formula': delta,
        'mu_Li_cancels': True,
        'scope': 'Diagnostic cached-energy arithmetic only; no changed score or thermal prediction',
    }


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--experiment',type=Path,required=True,help='Archived environment_v1/llzo directory')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    benchmark_path=ROOT/'data/benchmarks/environment_v1/lco_llzo_4v.json'
    table=json.loads(benchmark_path.read_text());manifest=json.loads((args.experiment/'experiment.json').read_text())
    verify_hash(table)
    assert table['sha256']==manifest['hashes']['benchmark_sha256']=='9bdef5811bafc0b24f6ae55140f74f0be592a0f4367ca253310e0544ebb8e060'
    assert manifest['budget']==10 and manifest['start_seed']==200 and manifest['repeats']==30
    rows=table['results'];good=[r for r in rows if r.get('acceptable')]
    flagged=[{k:r[k] for k in ('candidate_id','formula','penalty','self_decomposition_penalty','penalty_bin')} for r in good if r['formula'] in FLAGS]
    original_hashes=json.loads((args.experiment/'source_file_hashes.json').read_text())
    output={'analysis_status':'post-hoc descriptive annotation; frozen criterion and all primary results unchanged',
            'reviewed_experiment_commit':'06a4271','benchmark_sha256':table['sha256'],
            'flag_definition':FLAGS,'accepted_structures':len(good),
            'accepted_formulas':len({r['formula'] for r in good}),
            'flagged_accepted_structures':len(flagged),'flagged_accepted_formulas':len({r['formula'] for r in flagged}),
            'flagged_candidates':flagged,'arms':{},
            'source_sha256':{'benchmark_file':hashlib.sha256(benchmark_path.read_bytes()).hexdigest(),
                             'experiment_manifest':hashlib.sha256((args.experiment/'experiment.json').read_bytes()).hexdigest(),
                             'archive_hash_manifest':hashlib.sha256((args.experiment/'source_file_hashes.json').read_bytes()).hexdigest()}}
    for arm in ARMS:
        per_run=[];formulas=Counter();acceptable_formulas=Counter();ids=set();first_counts=Counter();hits_by_index=[0]*10
        hazard_mentions = 0
        for seed in range(200,230):
            name=f'{arm}_r{seed}.json';raw=(args.experiment/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==original_hashes[name]
            state=json.loads(raw);assert state['status']=='complete' and len(state['history'])==10
            hit=flagged_hit=unflagged_hit=0;first=None
            for i,h in enumerate(state['history']):
                r=h['result'];formula=r.get('formula');cid=h['proposal']['candidate_id']
                proposal_text = ' '.join(str(h['proposal'].get(k, '')) for k in ('hypothesis', 'motivation'))
                hazard_mentions += bool(HAZARD_TERMS.search(proposal_text))
                if formula:formulas[formula]+=1
                if isinstance(cid,str):ids.add(cid)
                if r.get('acceptable'):
                    hit+=1;acceptable_formulas[formula]+=1;hits_by_index[i]+=1
                    if first is None:first=i+1
                    if formula in FLAGS:flagged_hit+=1
                    else:unflagged_hit+=1
            first_counts[str(first) if first is not None else 'none']+=1
            per_run.append({'seed':seed,'acceptable_picks':hit,'flagged_acceptable_picks':flagged_hit,
                            'unflagged_acceptable_picks':unflagged_hit,'first_acceptable_query':first})
        output['arms'][arm]={'queries':300,'distinct_formulas':len(formulas),'distinct_ids':len(ids),
            'acceptable_picks':sum(r['acceptable_picks'] for r in per_run),
            'flagged_acceptable_picks':sum(r['flagged_acceptable_picks'] for r in per_run),
            'unflagged_acceptable_picks':sum(r['unflagged_acceptable_picks'] for r in per_run),
            'successful_runs':sum(r['acceptable_picks']>0 for r in per_run),
            'unflagged_hit_runs':sum(r['unflagged_acceptable_picks']>0 for r in per_run),
            'flagged_only_successful_runs':sum(r['acceptable_picks']>0 and r['unflagged_acceptable_picks']==0 for r in per_run),
            'first_hit_counts':dict(first_counts),'acceptable_picks_by_query_index':hits_by_index,
            'proposals_matching_limited_hazard_keywords': hazard_mentions,
            'hazard_keyword_regex': HAZARD_TERMS.pattern,
            'acceptable_formula_counts':dict(acceptable_formulas),'formula_counts':dict(formulas),
            'per_run':per_run}
    perch=next(r for r in good if r['formula']=='LiClO4')
    output['perchlorate_evaluator_evidence']={k:perch[k] for k in ('candidate_id','self_decomposition_penalty','penalty','contacts','absolute_contact_reaction_energies','endpoint_decomposition_penalties','objective')}
    output['diagnostic_cached_reaction'] = cached_perchlorate_reaction(table, perch['candidate_id'])
    assert output['flagged_accepted_structures']==5 and output['accepted_structures']==17
    assert output['arms']['random']['unflagged_hit_runs']==18 and output['arms']['iterative']['unflagged_hit_runs']==12
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(output,indent=2)+'\n')
    print('Flags:',len(flagged),'of',len(good),'accepted structures; primary data unchanged.')
    for arm,a in output['arms'].items():print(arm,a['distinct_formulas'],a['acceptable_picks'],a['successful_runs'],a['unflagged_hit_runs'])


if __name__=='__main__':main()
