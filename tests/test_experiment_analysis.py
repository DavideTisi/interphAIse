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


@pytest.mark.parametrize('field,value', [('allow_draft', True), ('benchmark_status', 'exploratory-exhaustive-not-frozen')])
def test_draft_run_metadata_is_rejected(tmp_path, field, value):
    directory = batch(tmp_path/'batch')
    path = directory/'experiment.json'
    manifest = json.loads(path.read_text())
    manifest[field] = value
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match='draft-table'):
        load_experiments([directory])


def test_draft_table_is_rejected_even_without_manifest_flag(tmp_path):
    from interphaise.tools.thermo_dataset import digest
    directory = batch(tmp_path/'batch')
    table = json.loads((ROOT/'data/benchmarks/coating_v3.json').read_text())
    table['status'] = 'exploratory-exhaustive-not-frozen'
    del table['sha256']
    table['sha256'] = digest(table)
    table_path = tmp_path/'draft.json'
    table_path.write_text(json.dumps(table))
    for path in (directory/'experiment.json', directory/'random_r00.json'):
        content = json.loads(path.read_text())
        content['hashes']['benchmark_sha256'] = table['sha256']
        path.write_text(json.dumps(content))
    with pytest.raises(ValueError, match='Draft benchmark'):
        load_experiments([directory], benchmark=table_path)
