import importlib.util
from pathlib import Path
import pytest
from interphaise.tools.thermo_dataset import digest,verify_hash

spec=importlib.util.spec_from_file_location('freeze',Path(__file__).resolve().parents[1]/'scripts/freeze_benchmark.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def draft():
    objective={'version':'v3-draft','contact_reference':'equilibrated'}
    data={'status':'draft-requires-scientific-review','objective':objective,
          'objective_sha256':digest(objective),'results':[{'status':'ok','objective':objective.copy(),'penalty':.2}]}
    data['sha256']=digest(data)
    return data


def test_freeze_preserves_numerics_and_source():
    source=draft()
    result=module.freeze(source,'v3.0','Team selected compatibility criterion')
    assert result['status']=='frozen' and source['status']!='frozen'
    assert result['results'][0]['penalty']==source['results'][0]['penalty']
    assert result['objective']['version']=='v3.0'
    assert result['frozen_from_sha256']==source['sha256']
    verify_hash(result)


def test_freeze_rejects_mixed_objectives():
    source=draft();source['results'][0]['objective']={'version':'other'}
    del source['sha256'];source['sha256']=digest(source)
    with pytest.raises(ValueError,match='Mixed'):module.freeze(source,'v3.0','reviewed')
