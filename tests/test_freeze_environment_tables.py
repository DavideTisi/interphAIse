from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

from interphaise.benchmark import BenchmarkQueries
from interphaise.tools.thermo_dataset import digest, verify_hash

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('freeze_env', ROOT/'scripts/freeze_environment_tables.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
POOL = ROOT/'data/exploration/environment_expansion_v1/pool.json'


def inputs():
    return json.loads(POOL.read_text()), [json.loads((ROOT/
        f'data/exploration/environment_expansion_v2/evaluation/{env}.json').read_text())
        for env in module.ENVIRONMENTS]


def rehash(value):
    value.pop('sha256', None)
    value['sha256'] = digest(value)


def test_real_freeze_preserves_all_science_and_loads_without_override(tmp_path):
    pool, sources = inputs()
    originals = deepcopy(sources)
    frozen = module.freeze_tables(pool, sources, decision='Reviewed inputs only', frozen_at='2026-10-21T00:00:00Z')
    assert sources == originals
    for source, table in zip(sources, frozen):
        verify_hash(table)
        assert table['frozen_from_sha256'] == source['sha256']
        assert table['sha256'] != source['sha256']
        for key, value in source.items():
            if key not in ('status', 'sha256'):
                assert table[key] == value
        path = tmp_path/(table['environment_id']+'.json')
        path.write_text(json.dumps(table))
        q = BenchmarkQueries(POOL, path, budget=10)
        assert len(q.available()) == 141
        failed = next(r for r in table['results'] if r['status'] == 'failed')
        assert q.query(failed['candidate_id']) == failed
        assert q.remaining == 9


@pytest.mark.parametrize('fault', ['hash', 'pool', 'objective', 'missing', 'duplicate', 'subset', 'frozen', 'dataset'])
def test_freeze_rejects_inconsistent_inputs(fault):
    pool, sources = inputs()
    table = sources[0]
    if fault == 'hash':
        table['voltage_V'] = 5
    elif fault == 'pool':
        table['pool_sha256'] = 'wrong'
    elif fault == 'objective':
        next(r for r in table['results'] if r['status'] == 'ok')['objective'] = {'version':'wrong'}
    elif fault == 'missing':
        table['results'].pop()
    elif fault == 'duplicate':
        table['results'][1] = deepcopy(table['results'][0])
    elif fault == 'subset':
        sources.pop()
    elif fault == 'frozen':
        table['status'] = 'frozen'
    elif fault == 'dataset':
        table['dataset_sha256'] = 'another snapshot'
    if fault != 'hash':
        rehash(table)
    with pytest.raises(ValueError):
        module.freeze_tables(pool, sources, decision='reviewed', frozen_at='2026-10-21T00:00:00Z')
