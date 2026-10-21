"""An explicit registry outside the historical grid must be evaluated and selected."""
import json
from pathlib import Path

import pytest

from scripts.run_petmad_interface import registry_points, select_registry


def test_historical_scan_and_selection_remain_unchanged():
    root=Path(__file__).resolve().parents[1]
    scan=json.loads((root/'data/petmad/cathode_thickness_v1/run_F4/registry_scan.json').read_text())
    assert registry_points()==[(*r['offset'],r['gap_A']) for r in scan]
    assert registry_points([0,.5,2])==registry_points()
    optimum,chosen=select_registry(scan)
    assert chosen is optimum and chosen==min(scan,key=lambda r:r['energy_eV'])


@pytest.mark.parametrize('requested',[(1/3,1/3,2.),(1/6,0.,2.)])
def test_distinct_requested_registry_is_added_once_and_selected(requested):
    points=registry_points(requested)
    assert len(points)==13 and points.count(requested)==1
    # The requested point must win selection even if another point has lower energy.
    scan=[dict(offset=[x,y],gap_A=gap,status='ok',energy_eV=float(i))
          for i,(x,y,gap) in enumerate(points)]
    optimum,chosen=select_registry(scan,requested)
    assert optimum is scan[0] and chosen is scan[-1]
    assert (*chosen['offset'],chosen['gap_A'])==requested


def test_rejected_requested_point_cannot_silently_use_scan_optimum():
    requested=(1/3,1/3,2.)
    scan=[dict(offset=[0,0],gap_A=2.,status='ok',energy_eV=-1.),
          dict(offset=list(requested[:2]),gap_A=2.,status='rejected',clashes=['overlap'])]
    with pytest.raises(ValueError,match='Requested registry .* rejected'):
        select_registry(scan,requested)
    with pytest.raises(ValueError,match='No valid registry'):
        select_registry(scan[1:])


@pytest.mark.parametrize('requested',[(float('nan'),0,2),(0,float('inf'),2),(0,0,0),(0,0,-1)])
def test_invalid_requested_registry_is_rejected_before_calculation(requested):
    with pytest.raises(ValueError,match='finite X, Y and a positive gap'):
        registry_points(requested)
