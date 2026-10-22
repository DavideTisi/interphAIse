"""Catch scientific disagreements between regenerated evidence and published slides."""
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.reproduce_results import read, verify_agreement

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def evidence():
    deck = read(ROOT / 'presentations/source/results_synthesis_2026-10-22.json')
    original = {'curves': {'acceptable': {arm: [deck['original'][arm]['curve'], None, 30]
                                          for arm in deck['arm_order']}}}
    return [read(ROOT / 'data/experiments/environment_v1/environment_summary.json'), original,
            read(ROOT / 'data/petmad/coating_comparison_v1/analysis_final/summary.json'),
            read(ROOT / 'data/experiments/llm_petmad_pilot_v1/report_live/assessment.json')]


def test_published_evidence_agrees(evidence):
    verify_agreement(*evidence)


@pytest.mark.parametrize('edit', ['environment', 'physical', 'forecast', 'order', 'accounting'])
def test_changed_scientific_claim_stops_reproduction(evidence, edit):
    env, original, physical, forecast = deepcopy(evidence)
    if edit == 'environment':
        env['environments']['Li7La3Zr2O12']['arms']['random']['acceptable'] = 0
    elif edit == 'physical':
        physical['cohort'][0]['contacts']['electrolyte']['W_adh_J_m2'] = 999
    elif edit == 'forecast':
        forecast['predictions'][1]['contacts']['cathode']['predicted'] = [0, 999]
    elif edit == 'order':
        forecast['decision_comparison']['changed'] = True
    else:
        physical['compute']['new']['calls'] -= 1
    with pytest.raises(ValueError):
        verify_agreement(env, original, physical, forecast)
