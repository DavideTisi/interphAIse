import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('evaluate_pool',Path(__file__).resolve().parents[1]/'scripts/evaluate_pool.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_random_baseline_counts_ties_and_failed_candidates():
    results=[{'candidate_id':str(i),'status':'ok','insulating':True,'penalty_bin':b,
              'penalty':b*.02,'acceptable':False,
              'endpoint_decomposition_penalties':{'electrode':0,'electrolyte':0}}
             for i,b in enumerate([1,1,3])]
    results.append({'candidate_id':'failed','status':'failed'})
    d=module.diagnostics(results)
    assert d['best_candidate_ids']==['0','1']
    assert d['random_best_bin_success'][1]['probability_find_best_bin']==.5
    assert d['random_best_bin_success'][2]['probability_find_best_bin']==pytest.approx(5/6)


def test_no_eligible_candidate_has_no_false_optimum():
    d=module.diagnostics([{'candidate_id':'failure','status':'failed'}])
    assert d['best_candidate_ids']==[] and d['best_bin'] is None
    assert d['random_best_bin_success'][-1]['probability_find_best_bin']==0
