#!/usr/bin/env python3
"""Export only six validated primary contacts for public/offline referee access.

This reads archived data; it makes no API request or new materials calculation.
The full catalogue is intentionally not published by this entry point.
"""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_structure_viewer import build_catalog, write_viewer


def referee_catalog(catalog):
    campaign = catalog.get('campaign')
    if not campaign or len(campaign['contacts']) != 6:
        raise ValueError('Referee export requires all six validated final contacts')
    if catalog['summary']['warnings']:
        raise ValueError('Resolve catalogue warnings before public export')
    contacts = campaign['contacts']
    identities = {(c['formula'], c['contact']) for c in contacts}
    expected = {(f, c) for f in ('LiNbF6', 'LiTaF6', 'LiCaAlF6')
                for c in ('cathode', 'electrolyte')}
    if identities != expected:
        raise ValueError('Unexpected coating/contact identities in final campaign')
    selected = {c['record_id'] for c in contacts}
    records = [deepcopy(r) for r in catalog['records'] if r['id'] in selected]
    if len(records) != 6 or len({r['id'] for r in records}) != 6:
        raise ValueError('Selected geometry missing or duplicated')
    for item in records:
        if item['state'] != 'relaxed' or not item.get('results') or not item.get('featured'):
            raise ValueError('Only validated selected relaxed contacts may be published')
    result = deepcopy(catalog)
    result['records'] = records
    result['comparisons'] = [c for c in result['comparisons']
                             if c['left'] in selected and c['right'] in selected]
    result['environments'] = {'lco_lpscl_4v': catalog['environments']['lco_lpscl_4v']}
    result['summary'].update(total=6, by_kind={'interface': 6}, candidate_ids=3,
                             interface_runs=6, calculated_runs=6)
    result['summary']['limitations'] = [
        'This compact export contains six selected primary interfaces: three coatings, each contacting LiCoO2 and Li6PS5Cl separately. It is not a complete three-layer cell or battery simulation.',
        'The geometries and primary values were available to the live LLM pilot. Sensitivity information was released afterwards and did not enter its choices.',
        'LiF was not selected and has no computed interface energy. It is not ranked by these calculations.',
        'All interfaces are formally polar and provisional. Lithium transport, reaction kinetics and battery cycling were not tested.',
        'The LiNbF6–LiTaF6 weaker-contact difference is smaller than documented construction sensitivities. These numbers do not establish a robust materials ranking.',
        'LiCaAlF6 electrolyte thickness and bulk-structure sensitivity remain unquantified. Its sampled electrolyte registries span approximately 0.52–0.74 J/m².',
        'The post-decision alternative-bulk electrolyte shifts are −0.121 J/m² for LiNbF6 and −0.114 J/m² for LiTaF6. They combine construction effects and are not statistical error bars.',
        'Contact registry selection follows the lowest relaxed joined energy, not maximum adhesion. Sphere sizes are illustrative; displayed bonds are not inferred.',
    ]
    result['campaign']['note'] = ('LiF: not selected, no interface energy computed. '
        'LiCaAlF6 electrolyte thickness and bulk-structure sensitivity: unquantified. '
        'Both contacts are formally polar; these are model results, not measured adhesion.')
    result['edition'] = 'referee'
    return result


def validate_public_text(text):
    """Public export contains no local paths, credential syntax or remote assets."""
    forbidden = [r'/Users/', r'/home/', r'(?i)sk-ant-[a-z0-9_-]+',
                 r'github_pat_[a-zA-Z0-9_]+', r'gh[pousr]_[a-zA-Z0-9]{20,}',
                 r'(?i)(?:api[_-]?key|authorization)\s*[=:]\s*["\']?[^\s"\']{12,}',
                 r'<script[^>]+\bsrc\s*=', r'\bfetch\s*\(',
                 r'(?i)(?:src|href)\s*=\s*["\']https?://']
    for pattern in forbidden:
        if re.search(pattern, text):
            raise ValueError(f'Public export safety check failed: {pattern}')


def build_site(output, catalog=None, root=ROOT):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    # Never copy a repository directory to a public website: write a fixed allowlist.
    allowed = {'index.html', 'evidence.json', 'README.txt', '.nojekyll',
               'interphaise-referee-viewer.zip'}
    if any(p.name not in allowed for p in output.iterdir()):
        raise ValueError('Output must be empty or contain only the referee export files')
    compact = referee_catalog(catalog if catalog is not None else build_catalog(root=root))
    validate_public_text(json.dumps(compact))
    html_path = output / 'index.html'
    write_viewer(compact, html_path)
    validate_public_text(html_path.read_text())
    try:
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        revision = None
    evidence = {
        'edition': 'referee', 'source_revision': revision,
        'source_revision_note': 'Checkout revision at export; exact exporter/template hashes are recorded below.',
        'final_index': compact['campaign']['index'],
        'html_sha256': hashlib.sha256(html_path.read_bytes()).hexdigest(),
        'builder_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'template_sha256': hashlib.sha256((root / 'scripts/viewer/template.html').read_bytes()).hexdigest(),
        'published_geometry_count': 6,
        'contacts': [{**contact, 'source_geometry': next(r['provenance'][0] for r in compact['records']
                                                       if r['id'] == contact['record_id'])}
                     for contact in compact['campaign']['contacts']],
        'not_computed': ['LiF interface energies'],
        'limits': compact['summary']['limitations'],
        'new_calculations': False,
    }
    (output / 'evidence.json').write_text(json.dumps(evidence, indent=2, allow_nan=False) + '\n')
    (output / '.nojekyll').write_text('')
    (output / 'README.txt').write_text(
        'interphAIse — referee structure explorer\n\n'
        'Open index.html in an ordinary browser with JavaScript enabled.\n'
        'No installation, login, API key, server or internet connection is required.\n'
        'Choose LiNbF6, LiTaF6 or LiCaAlF6 to compare its two separately calculated contacts.\n'
        'Drag to rotate; scroll to zoom; use Colour to distinguish coating and substrate.\n'
        'Save XYZ exports exact archived geometry; Save PNG exports the visible panel.\n\n'
        'The hosted edition and this offline file contain the same six interfaces.\n'
        'evidence.json records the final-index and geometry hashes, values and limitations.\n'
        'The complete 460-geometry catalogue can be rebuilt from the project repository with:\n'
        '    python scripts/build_structure_viewer.py\n'
        'The compact edition is rebuilt with:\n'
        '    python scripts/build_referee_viewer.py --output runs/referee-site\n\n'
        'All interfaces are formally polar, provisional model results. LiF is uncomputed.\n'
        'Later sensitivity results did not enter the live LLM decisions.\n'
        'Lithium transport and battery cycling were not evaluated.\n')
    files = sorted(p for p in output.iterdir() if p.name != 'interphaise-referee-viewer.zip')
    for path in files:
        validate_public_text(path.read_text())
    archive_path = output / 'interphaise-referee-viewer.zip'
    with zipfile.ZipFile(archive_path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            # Stable timestamps and filenames make the download easy to compare/reproduce.
            info = zipfile.ZipInfo(path.name, (2026, 10, 22, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'runs/referee-site')
    args = parser.parse_args()
    build_site(args.output)
    print(f'Wrote six validated interfaces to {args.output}; no network calls or new calculations.')


if __name__ == '__main__':
    main()
