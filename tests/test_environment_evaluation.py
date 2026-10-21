from copy import deepcopy
from itertools import combinations
import json

import pytest

from scripts.fetch_environment_dataset import (
    merge_entries, source_for_version, validate_coverage, write_hashed,
)
from scripts.evaluate_environment_expansion import (
    component_summary, diagnostics, success_probability, compare_environments,
)
from interphaise.tools.thermo_dataset import THERMO_TYPE, verify_hash


def row(i, penalty_bin=None, acceptable=False):
    out = {'candidate_id':f'mp-{i}', 'formula':'LiF',
           'status':'ok' if penalty_bin is not None else 'failed',
           'insulating':penalty_bin is not None, 'acceptable':acceptable,
           'penalty_bin':penalty_bin}
    if penalty_bin is not None:
        out['penalty'] = penalty_bin*.02
        out['component_analysis'] = {'dominant_components':['coating_self']}
    return out


def test_different_database_never_reuses_entries():
    source = {'db_version':'old', 'thermo_type':THERMO_TYPE}
    assert source_for_version(source, 'new') is None
    assert source_for_version(source, 'old') is source
    assert source_for_version({**source, 'thermo_type':'R2SCAN'}, 'old') is None


def test_conflicting_duplicate_corrected_entries_rejected():
    entry = {'entry_id':'entry1', 'energy':-2, 'data':{'thermo_type':THERMO_TYPE,'run_type':'GGA'}}
    store = {}; merge_entries(store, [entry, deepcopy(entry)])
    assert len(store) == 1
    with pytest.raises(ValueError, match='Conflicting'):
        merge_entries(store, [{**entry, 'energy':-3}])
    with pytest.raises(ValueError, match='functional'):
        merge_entries({}, [{**entry, 'data':{**entry['data'], 'run_type':'R2SCAN'}}])


def test_complete_coverage_required_even_with_pinned_entries():
    pool = {'sha256':'pool', 'candidates':[{'formula':'LiF'}]}
    plan = {'sha256':'plan', 'environments':[{'endpoints':{
        'electrode':{'formula':'LiF'}, 'electrolyte':{'formula':'LiF'}}}]}
    dataset = {'pool_sha256':'pool', 'plan_sha256':'plan', 'batches':[{'systems':['Li','F']}]}
    with pytest.raises(ValueError, match='Incomplete'):
        validate_coverage(pool, plan, dataset)
    dataset['batches'][0]['systems'].append('F-Li')
    assert validate_coverage(pool, plan, dataset) == 3


def test_exact_random_and_conditional_regret_match_enumeration():
    rows = [row(1,0,True),row(2,2),row(3,2),row(4)]
    diag = diagnostics(rows)
    for k in range(1,5):
        draws = list(combinations(rows,k))
        best = [min((r['penalty_bin'] for r in draw if r['insulating']), default=None) for draw in draws]
        curve = diag['exact_random_without_replacement'][k]
        assert curve['probability_no_eligible_result'] == pytest.approx(sum(v is None for v in best)/len(draws))
        assert curve['probability_acceptable'] == pytest.approx(sum(v == 0 for v in best)/len(draws))
        valid = [v for v in best if v is not None]
        assert curve['expected_best_bin_regret_conditional_on_eligible'] == pytest.approx(sum(valid)/len(valid))


def test_no_eligible_candidates_has_no_invented_optimum_or_median():
    diag = diagnostics([row(1),row(2)])
    assert diag['best_bin'] is None and diag['best_ids'] == []
    for step in diag['exact_random_without_replacement']:
        assert step['median_best_bin'] is None
        assert step['probability_best_bin'] == step['probability_acceptable'] == 0
        assert step['probability_no_eligible_result'] == 1
        assert step['expected_best_bin_regret_conditional_on_eligible'] is None
    assert diag['fluorides_first']['first_optimum_bin_query'] is None


def test_sparse_eligibility_median_does_not_raise_and_zero_acceptable_is_valid():
    diag = diagnostics([row(1,3),row(2),row(3),row(4)])
    assert diag['exact_random_without_replacement'][1]['median_best_bin'] is None
    assert diag['exact_random_without_replacement'][2]['median_best_bin'] == 3
    assert diag['acceptable'] == 0
    assert diag['fluorides_first']['first_acceptable_query'] is None


def test_components_count_ties_without_arbitrary_precedence():
    summary = component_summary({'self_decomposition_penalty':.04,
        'contact_reaction_energies':[-.04,-.01], 'penalty':.04})
    assert summary['dominant_components'] == ['coating_self','cathode_contact']


def test_comparison_handles_constant_bins_and_detects_reversal():
    packages = []
    for name, rows in [('a',[row(1,0),row(2,1)]), ('b',[row(1,1),row(2,0)]),
                       ('c',[row(1,0),row(2,0)])]:
        packages.append({'environment_id':name,'results':rows,'diagnostics':diagnostics(rows)})
    comparisons = compare_environments(packages)
    assert comparisons[0]['candidate_pair_order_counts']['reversed'] == 1
    assert comparisons[0]['spearman_binned_penalty'] == pytest.approx(-1)
    assert comparisons[1]['spearman_binned_penalty'] is None


def test_hashed_output_roundtrip_and_invalid_budget(tmp_path):
    p = tmp_path/'test.json'
    write_hashed(p, {'bins':{2:1,10:4}})
    verify_hash(json.loads(p.read_text()))
    with pytest.raises(ValueError):
        success_probability(4,5,1)
