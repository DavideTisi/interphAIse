"""F2: derived work values only from valid runs computed with the same checkpoint."""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest
from ase.io import read, write

from interphaise.tools.provenance import ProvenanceError, load_valid_interface_run, require_matching_checkpoint

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'data/petmad/niflheim_batch1/cathode_ref'
SHA = '3f52e97c459b2a28a94fc49b8a2f9a92551231a0ea4f5b5db2396f12d8ffa1e9'


@pytest.fixture
def run(tmp_path):
    dest = tmp_path / 'cathode_ref'
    shutil.copytree(ARCHIVE, dest)
    return dest


def edit_json(path, change):
    data = json.loads(path.read_text())
    change(data)
    path.write_text(json.dumps(data))


def test_archived_run_with_matching_checkpoint_is_accepted(run):
    valid = load_valid_interface_run(run, SHA)
    assert len(valid['finals']['interface']) == 696 and np.isclose(valid['area_A2'], 88.8, atol=1e-3)


def test_wrong_or_missing_checkpoint_hash_is_refused(run):
    with pytest.raises(ProvenanceError, match='does not match'):
        load_valid_interface_run(run, '0' * 64)
    with pytest.raises(ProvenanceError):
        require_matching_checkpoint(SHA, {'bulk summary.json': None})


@pytest.mark.parametrize('corrupt, message', [
    (lambda run: edit_json(run / 'relaxation_records.json', lambda d: d['film'].update(converged=False)), 'unconverged'),
    (lambda run: edit_json(run / 'relaxation_records.json', lambda d: d['substrate'].update(final_energy_eV=float('nan'))),
     'non-finite'),
    (lambda run: edit_json(run / 'result.json', lambda d: d.update(numerically_valid=False)), 'not numerically valid'),
    (lambda run: edit_json(run / 'result.json', lambda d: d.update(area_A2=90.0)), 'area'),
])
def test_invalid_source_runs_are_refused(run, corrupt, message):
    corrupt(run)
    with pytest.raises(ProvenanceError, match=message):
        load_valid_interface_run(run, SHA)


def test_fragment_labels_must_match_saved_references(run):
    initial = read(run / 'initial.extxyz')
    labels = initial.arrays['interface_label'].copy()
    film = np.where(labels == 'film')[0]
    labels[film[0]] = 'substrate'   # one coating atom mislabelled as substrate
    initial.arrays['interface_label'] = labels
    write(run / 'initial.extxyz', initial)
    with pytest.raises(ProvenanceError, match='fragment'):
        load_valid_interface_run(run, SHA)


@pytest.mark.parametrize('script', ['fixed_geometry_separation', 'vacuum_check'])
def test_scripts_refuse_a_different_checkpoint_before_loading_the_model(run, tmp_path, monkeypatch, script):
    fake = tmp_path / 'pet-mad-s-v1.6.0.ckpt'
    fake.write_bytes(b'not the pinned checkpoint')
    before = sorted(p.name for p in run.iterdir())
    module = __import__(f'scripts.{script}', fromlist=['main'])
    monkeypatch.setattr(sys, 'argv', [script, str(run), '--checkpoint', str(fake)])
    with pytest.raises(SystemExit):
        module.main()
    assert sorted(p.name for p in run.iterdir()) == before   # nothing written


def test_multistart_refuses_a_different_checkpoint_before_writing(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'scripts'))   # the script imports a sibling script module
    from scripts import multistart_bulk
    fake = tmp_path / 'pet-mad-s-v1.6.0.ckpt'
    fake.write_bytes(b'not the pinned checkpoint')
    out = tmp_path / 'out'
    monkeypatch.setattr(sys, 'argv', ['multistart_bulk', 'Li6PS5Cl', '--output', str(out), '--checkpoint', str(fake)])
    with pytest.raises(SystemExit):
        multistart_bulk.main()
    assert not out.exists()
