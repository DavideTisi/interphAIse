"""Check the alternate agent backend without importing real providers."""
import importlib.util
import sys
import types
from pathlib import Path

import pytest


def test_backend_only_registers_haiku_and_rejects_other_models(monkeypatch):
    captured = []
    class Router:
        def __init__(self, **kwargs):
            captured.append(kwargs)
        def completion(self, **kwargs):
            pytest.fail('No real call expected')
    module = types.ModuleType('litellm.router')
    module.Router = Router
    monkeypatch.setitem(sys.modules, 'litellm', types.ModuleType('litellm'))
    monkeypatch.setitem(sys.modules, 'litellm.router', module)
    path = Path(__file__).resolve().parents[1] / 'interphaise' / 'backends.py'
    spec = importlib.util.spec_from_file_location('backend_under_test', path)
    backend = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backend)
    models = captured[0]['model_list']
    assert len(models) == 1
    assert models[0]['litellm_params']['model'] == 'anthropic/claude-haiku-5-5'
    assert callable(backend.router_chat('claude-haiku'))
    for model in ['claude-sonnet', 'deepseek-v3.2', 'gpt-5-mini']:
        with pytest.raises(ValueError, match='restricted'):
            backend.router_chat(model)
        with pytest.raises(ValueError, match='restricted'):
            backend._call_router(model, 'system', 'user')
