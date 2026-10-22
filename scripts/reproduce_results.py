#!/usr/bin/env python3
"""Reproduce published analyses offline; write only under runs/, never launch live work."""
import argparse
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
CAMPAIGN = Path('data/petmad/coating_comparison_v1')
PILOT = Path('data/experiments/llm_petmad_pilot_v1')
ENV = Path('data/experiments/environment_v1')
DECK = Path('presentations/source/results_synthesis_2026-10-22.json')


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def evidence_hashes():
    # Includes the unchanged live prompts/responses, frozen tables and saved physics.
    return {str(p.relative_to(ROOT)): sha(p) for p in sorted((ROOT / 'data').rglob('*'))
            if p.is_file() and p.suffix in {'.json', '.gz', '.extxyz'}}


def verify_agreement(environment, original, physical, assessment, *, viewer=None, deck=None):
    deck = read(ROOT / DECK) if deck is None else deck
    for env, expected in deck['environments'].items():
        for arm, count in expected['counts'].items():
            require(environment['environments'][env]['arms'][arm]['acceptable'] == count,
                    f'Presentation / environment disagreement: {env} / {arm}')
    for arm in deck['arm_order']:
        curve = original['curves']['acceptable'][arm]
        require(round(curve[0][-1] * curve[2]) == deck['original'][arm]['count'],
                f'Presentation / original benchmark disagreement: {arm}')
    require(not physical['invalid_runs'], 'Invalid physical evidence')
    require(physical['compute']['new']['calls'] == 6632, 'New calculator-call total changed')
    require(len(physical['consistency']) == 4, 'Missing consistency records')
    require(len(physical['not_selected_runs']) == 12, 'Missing unselected LiF records')
    for row in physical['cohort']:
        for contact, values in row['contacts'].items():
            require(values['status'] == 'validated', f'Incomplete contact: {row["formula"]} / {contact}')
            for metric in ('W_adh_J_m2', 'W_sep_J_m2'):
                expected = deck['physical'][row['formula']]['contacts'][contact][metric]
                require(math.isclose(values[metric], expected, abs_tol=1e-9, rel_tol=0),
                        f'Presentation / physical disagreement: {row["formula"]} / {contact} / {metric}')
    predictions = {r['formula']: r for r in assessment['predictions']}
    for forecast in deck['forecast']:
        check = predictions[forecast['coating']]['contacts'][forecast['contact']]
        require(check['predicted'] == forecast['range'], 'Prospective forecast range changed')
        require(math.isclose(check['observed'], forecast['observed'], abs_tol=1e-9, rel_tol=0),
                'Forecast outcome changed')
    require(assessment['decision_comparison']['changed'] is False, 'Pilot choice order changed')
    if viewer:
        require(len(viewer['campaign']['contacts']) == 6, 'Viewer must show six selected contacts')
        for contact in viewer['campaign']['contacts']:
            expected = deck['physical'][contact['formula']]['contacts'][contact['contact']]
            for metric in ('W_adh_J_m2', 'W_sep_J_m2'):
                require(math.isclose(contact[metric], expected[metric], abs_tol=1e-6, rel_tol=0),
                        f'Viewer / presentation disagreement: {contact["formula"]} / {metric}')
        require(viewer['campaign']['not_selected'] == ['LiF'], 'Viewer must keep LiF uncomputed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('runs/reproduced_results'))
    parser.add_argument('--skip-viewer', action='store_true', help='Skip the larger offline HTML export')
    args = parser.parse_args()
    out = (ROOT / args.output).resolve()
    require(out.is_relative_to(ROOT / 'runs'), 'Output must be inside this checkout’s runs/ directory')
    for package, version in [('pymatgen', '2026.9.24'), ('pymatgen-core', '2026.10.16')]:
        require(importlib.metadata.version(package) == version, f'Install pinned {package}=={version}')
    out.mkdir(parents=True, exist_ok=True)
    before = evidence_hashes()
    executed = []
    child_env = dict(os.environ, PYTHONPATH=str(ROOT), MPLCONFIGDIR=str(out / '.matplotlib'))
    # These commands read archived results. No runner, API client, checkpoint or cluster command is invoked.
    def run(name, *args):
        command = [sys.executable, *map(str, args)]
        with (out / f'{name}.log').open('w') as log:
            subprocess.run(command, cwd=ROOT, env=child_env, stdout=log, stderr=subprocess.STDOUT, check=True)
        executed.append(command[1:])
        print(f'{name}: passed', flush=True)
    run('original', 'scripts/analyse_discovery_experiment.py',
        'data/experiments/integrated_v3_20261021_s100', 'data/experiments/shuffled_v3_20261021_s100',
        '--benchmark', 'data/benchmarks/coating_v3.json', '--summary', out / 'original.json',
        '--plot', out / 'original.png')
    for name in ('integrated_v3_20261021_s100', 'shuffled_v3_20261021_s100'):
        run('replay_' + name, 'scripts/audit_discovery_batch.py', Path('data/experiments') / name,
            '--output', out / f'replay_{name}.json')
    run('environment', 'scripts/analyse_environment_study.py', ENV / 'lpscl', ENV / 'lic', ENV / 'llzo',
        '--production', '--json', out / 'environment.json')
    run('physical', 'scripts/analyse_mlip_comparison.py', '--index', CAMPAIGN / 'index_final.json',
        '--out', out / 'physical')
    run('pilot', 'scripts/report_llm_petmad_pilot.py', '--state', PILOT / 'state.json', '--out', out / 'pilot')
    catalog = None
    if not args.skip_viewer:
        from scripts.build_structure_viewer import build_catalog, write_viewer
        catalog = build_catalog()
        require(not catalog['summary']['warnings'], 'Viewer omitted invalid or missing evidence')
        write_viewer(catalog, out / 'structure_viewer.html')
        print('viewer: passed', flush=True)
    verify_agreement(read(out / 'environment.json'), read(out / 'original.json'),
                     read(out / 'physical/summary.json'), read(out / 'pilot/assessment.json'), viewer=catalog)
    final = read(ROOT / CAMPAIGN / 'index_final.json')
    decision = read(ROOT / CAMPAIGN / 'index.json')
    primary = lambda obj: {r['run_id']: r for r in obj['runs'] if r['role'] == 'primary' and r['status'] == 'valid'}
    require(primary(final) == primary(decision), 'Decision-time primaries changed in final release')
    require(len(primary(final)) == 17, 'Expected 17 evaluated primary rows')
    for snapshot in final['decision_snapshots']:
        expected = snapshot.get('index_sha256') or snapshot.get('bundle_sha256')
        require(sha(ROOT / snapshot['path']) == expected, 'Decision snapshot hash changed')
    require(sha(ROOT / CAMPAIGN / 'index_final.json') == read(ROOT / DECK)['sources']['final_index_sha256'],
            'Presentation refers to a different final index')
    require(before == evidence_hashes(), 'A frozen evidence file changed during reproduction')
    receipt = dict(status='passed', offline=True, commands=executed, evidence_files_unchanged=len(before),
                   selected_contacts=6, evaluated_primary_rows=17, new_calculator_calls=6632,
                   viewer_checked=catalog is not None, final_index_sha256=sha(ROOT / CAMPAIGN / 'index_final.json'),
                   source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                   source_code_sha256={str(p.relative_to(ROOT)): sha(p) for folder in ('scripts', 'interphaise')
                                       for p in sorted((ROOT / folder).rglob('*.py'))},
                   packages={p: importlib.metadata.version(p) for p in ('pymatgen', 'pymatgen-core', 'numpy', 'ase', 'matplotlib')})
    (out / 'VERIFICATION.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(f'All analyses agree; frozen evidence unchanged. Outputs: {out}')


if __name__ == '__main__':
    main()
