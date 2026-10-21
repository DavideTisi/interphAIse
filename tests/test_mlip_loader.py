"""Protect explicit model routing without downloading checkpoints."""
import sys
import types

import pytest

from interphaise.tools.mlip import load_mlip


def test_upet_receives_exact_checkpoint(monkeypatch):
    calls = []
    calculator = object()
    module = types.ModuleType('upet.ase')
    def factory(**kwargs):
        calls.append(kwargs)
        return calculator
    module.UPETCalculator = factory
    monkeypatch.setitem(sys.modules, 'upet', types.ModuleType('upet'))
    monkeypatch.setitem(sys.modules, 'upet.ase', module)
    assert load_mlip('upet:pet-mad-s@1.6.0', device='cpu') is calculator
    assert calls == [{'model': 'pet-mad-s', 'version': '1.6.0', 'device': 'cpu'}]


@pytest.mark.parametrize('spec', ['upet:pet-mad-s', 'upet:@1.6.0',
                                  'upet:pet-mad-s@', 'upet:pet-mad-s@latest',
                                  'upet:pet-mad-s@1.6.0@other'])
def test_upet_requires_explicit_version(spec):
    with pytest.raises(ValueError, match='explicit UPET checkpoint'):
        load_mlip(spec, device='cpu')


def test_upet_auto_device_uses_cpu_on_apple(monkeypatch):
    from interphaise.tools import mlip
    monkeypatch.setattr(mlip, 'best_device', lambda: 'mps')
    module = types.ModuleType('upet.ase')
    module.UPETCalculator = lambda **kwargs: kwargs
    monkeypatch.setitem(sys.modules, 'upet', types.ModuleType('upet'))
    monkeypatch.setitem(sys.modules, 'upet.ase', module)
    assert load_mlip('upet:pet-mad-s@1.6.0')['device'] == 'cpu'
    assert load_mlip('upet:pet-mad-s@1.6.0', device='mps')['device'] == 'mps'
