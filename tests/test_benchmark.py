import json
import pytest
from interphaise.benchmark import BenchmarkQueries
from interphaise.tools.thermo_dataset import digest


def fixture_files(tmp_path,status='frozen'):
    pool={'candidates':[{'candidate_id':i,'formula':'LiF','family':'halide','band_gap_eV':9,
                         'summary_energy_above_hull_eV_atom':0} for i in ('one','two')]}
    pool['sha256']=digest(pool)
    benchmark={'status':status,'pool_sha256':pool['sha256'],'objective':{'version':'synthetic'},
               'objective_sha256':digest({'version':'synthetic'}),'endpoints':{},'voltage_V':4,
               'results':[{'candidate_id':'one','status':'ok','penalty':.1},
                          {'candidate_id':'two','status':'failed','error':'Missing entry'}]}
    benchmark['sha256']=digest(benchmark)
    for name,data in [('pool',pool),('benchmark',benchmark)]:
        (tmp_path/name).write_text(json.dumps(data))
    return tmp_path/'pool',tmp_path/'benchmark'


def test_public_metadata_and_history_do_not_leak(tmp_path):
    q=BenchmarkQueries(*fixture_files(tmp_path),budget=2)
    assert q.history()==[]
    assert set(q.available()[0])=={'candidate_id','formula','family'}
    assert 'results' not in q.task() and 'diagnostics' not in q.task()
    r=q.query('one');r['penalty']=999
    assert q.history()[0]['penalty']==.1
    assert [c['candidate_id'] for c in q.available()]==['two']
    q.query('two')
    assert q.remaining==0 and q.history()[-1]['status']=='failed'
    with pytest.raises(ValueError,match='exhausted'):q.query('one')


def test_drafts_refused_and_unknown_attempt_charged(tmp_path):
    paths=fixture_files(tmp_path,status='draft')
    with pytest.raises(ValueError,match='Draft'):BenchmarkQueries(*paths,budget=2)
    q=BenchmarkQueries(*paths,budget=2,allow_draft=True)
    assert q.query('not-real')['status']=='failed' and q.remaining==1
    q.query('one')
    assert q.remaining==0


def test_duplicate_charged_without_revealing_new_result(tmp_path):
    q=BenchmarkQueries(*fixture_files(tmp_path),budget=2)
    q.query('one')
    assert q.query('one')['status']=='failed'
    assert [r['candidate_id'] for r in q.history()]==['one','one']


def test_invalid_id_type_consumes_budget(tmp_path):
    q=BenchmarkQueries(*fixture_files(tmp_path),budget=1)
    assert q.query(['one'])['status']=='failed'
    assert q.remaining==0
