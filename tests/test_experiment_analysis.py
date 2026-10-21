import json
from pathlib import Path

import pytest

from interphaise.benchmark import BenchmarkQueries
from interphaise.discovery import run_discovery, PROMPT_VERSION
from scripts.analyse_discovery_experiment import load_experiments

ROOT = Path(__file__).resolve().parents[1]


def batch(directory, seed=0):
    directory.mkdir()
    q = BenchmarkQueries(ROOT/'data/pools/mp_candidates_v2.json',
                         ROOT/'data/benchmarks/coating_v3.json', budget=2)
    state = run_discovery(q, strategy='random', seed=seed, output=directory/f'random_r{seed:02d}.json')
    manifest = dict(arms=['random'], repeats=1, start_seed=seed, budget=2,
                    hashes=state['hashes'], prompt_version=PROMPT_VERSION,
                    benchmark='data/benchmarks/coating_v3.json', model=None,
                    temperature=1., max_tokens=4096)
    (directory/'experiment.json').write_text(json.dumps(manifest))
    return directory


def test_missing_run_is_error_not_smaller_denominator(tmp_path):
    directory = batch(tmp_path/'batch')
    (directory/'random_r00.json').unlink()
    with pytest.raises(ValueError, match='missing='):
        load_experiments([directory])


def test_extensions_combine_but_reruns_require_explicit_replacement(tmp_path):
    a, b, c = batch(tmp_path/'a'), batch(tmp_path/'b', seed=1), batch(tmp_path/'c')
    _, _, runs, _ = load_experiments([a,b])
    assert [r['seed'] for r in runs['random']] == [0,1]
    with pytest.raises(ValueError, match='Duplicate'):
        load_experiments([a,c])
    _, _, runs, notes = load_experiments([a,c], replace_duplicates=True)
    assert len(runs['random'])==1 and notes[0]['seed']==0


def test_setting_mismatch_and_wrong_benchmark_are_rejected(tmp_path):
    a,b = batch(tmp_path/'a'),batch(tmp_path/'b',seed=1)
    path = b/'experiment.json'
    m = json.loads(path.read_text());m['temperature']=0.;path.write_text(json.dumps(m))
    with pytest.raises(ValueError, match='settings differ'):
        load_experiments([a,b])
    with pytest.raises(ValueError, match='benchmark hash'):
        load_experiments([a], benchmark=ROOT/'data/benchmarks/coating_v2_diagnostic.json')


def test_unfinished_run_cannot_be_analysed_as_failure(tmp_path):
    directory = batch(tmp_path/'batch');path=directory/'random_r00.json'
    run=json.loads(path.read_text());run['status']='running';path.write_text(json.dumps(run))
    with pytest.raises(ValueError, match='unfinished'):
        load_experiments([directory])


def test_exact_median_is_inf_when_eligible_candidates_are_sparse():
    from scripts.analyse_discovery_experiment import exact_median_best_bin
    ok = lambda b: {'status': 'ok', 'insulating': True, 'penalty_bin': b}
    bad = {'status': 'failed'}
    sparse = [ok(1), ok(4)] + [bad] * 8          # 2 of 10 eligible
    # k=1,2: P(any eligible) = 0.2, 0.38 < 0.5; k=3: P(bin<=4) = 1 - C(8,3)/C(10,3) = 0.53;
    # k=5: P(bin<=1) = 1 - C(9,5)/C(10,5) = 0.5
    assert exact_median_best_bin(sparse, 5) == [float('inf'), float('inf'), 4, 4, 1]
    assert exact_median_best_bin([bad] * 6, 3) == [float('inf')] * 3
