"""Protect the bounded public export and its link to validated evidence."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile

import pytest

from scripts.build_referee_viewer import build_site, referee_catalog, validate_public_text
from scripts.build_structure_viewer import build_catalog


@pytest.fixture(scope='module')
def full_catalog():
    return build_catalog()


def test_referee_export_preserves_six_selected_geometries_and_metrics(full_catalog):
    compact = referee_catalog(full_catalog)
    originals = {r['id']: r for r in full_catalog['records']}
    assert len(compact['records']) == 6
    assert len(compact['comparisons']) == 3
    assert compact['summary']['candidate_ids'] == 3
    for item in compact['records']:
        assert item == originals[item['id']]
        assert item['campaign_role'] == 'Selected primary · available to the live pilot'
    assert compact['campaign']['not_selected'] == ['LiF']
    assert 'unquantified' in compact['campaign']['note']
    assert all(c['left'] in originals and c['right'] in originals for c in compact['comparisons'])
    assert len(full_catalog['records']) > 6  # Input was not mutated.


@pytest.mark.parametrize('problem', ['missing', 'duplicate', 'warning', 'unrelaxed'])
def test_incomplete_or_invalid_public_bundle_is_rejected(full_catalog, problem):
    corrupted = deepcopy(full_catalog)
    selected_id = corrupted['campaign']['contacts'][0]['record_id']
    selected = next(r for r in corrupted['records'] if r['id'] == selected_id)
    if problem == 'missing':
        corrupted['records'].remove(selected)
    elif problem == 'duplicate':
        corrupted['records'].append(deepcopy(selected))
    elif problem == 'warning':
        corrupted['summary']['warnings'].append('Missing source evidence')
    else:
        selected['state'] = 'initial'
    with pytest.raises(ValueError):
        referee_catalog(corrupted)


def test_download_is_self_contained_and_exactly_matches_hosted_file(full_catalog, tmp_path):
    evidence = build_site(tmp_path, catalog=full_catalog)
    assert {p.name for p in tmp_path.iterdir()} == {
        'index.html', 'evidence.json', 'README.txt', '.nojekyll', 'interphaise-referee-viewer.zip'}
    html = (tmp_path / 'index.html').read_text()
    assert '__STRUCTURES_JSON__' not in html
    assert '<script src=' not in html and 'fetch(' not in html
    assert len(html.encode()) < 3_000_000
    assert evidence['html_sha256'] == hashlib.sha256((tmp_path / 'index.html').read_bytes()).hexdigest()
    with zipfile.ZipFile(tmp_path / 'interphaise-referee-viewer.zip') as archive:
        assert archive.read('index.html') == (tmp_path / 'index.html').read_bytes()
        assert json.loads(archive.read('evidence.json')) == evidence
        assert len(archive.namelist()) == 4


@pytest.mark.parametrize('text', ['/Users/person/project', '/home/someone/file',
                                 '<script src="https://remote.test/a.js">',
                                 'fetch("https://remote.test")',
                                 'api_key="public-export-must-never-have-this"'])
def test_private_paths_and_remote_dependencies_are_rejected(text):
    with pytest.raises(ValueError):
        validate_public_text(text)


def test_never_publish_an_unrelated_directory(full_catalog, tmp_path):
    (tmp_path / '.env').write_text('must remain private')
    with pytest.raises(ValueError, match='empty or contain only'):
        build_site(tmp_path, catalog=full_catalog)
    assert not (tmp_path / 'index.html').exists()
