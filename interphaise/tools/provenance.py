"""Provenance gates for calculations derived from saved PET-MAD runs (review finding F2).

Derived quantities (rigid separation, vacuum checks, multistart comparisons) subtract newly
computed energies from saved ones. They are only meaningful if both come from the same model
checkpoint and the saved runs are numerically valid. These checks run before a calculator is
loaded, so a mismatch fails fast and writes nothing.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from ase.io import read


class ProvenanceError(ValueError):
    """A saved reference cannot be combined with a new calculation.

    ``kind`` separates the two situations consumers must treat differently:
    ``'integrity'`` (wrong checkpoint, inconsistent or missing files, labels, cell or area) means the
    evidence package itself is invalid and must block use until resolved; ``'calculation'``
    (unconverged or non-finite relaxation, overlaps) is a genuine completed outcome of the calculation.
    """

    def __init__(self, message, kind='integrity'):
        super().__init__(message)
        self.kind = kind


def checkpoint_sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require_matching_checkpoint(supplied: str, saved: dict[str, str | None]) -> None:
    """Every saved energy reference must carry exactly the supplied checkpoint hash.

    A missing hash is a mismatch: matching a filename is not provenance.
    """
    bad = {name: value for name, value in saved.items() if value != supplied}
    if bad:
        raise ProvenanceError(f"checkpoint {supplied[:12]}… does not match saved references {bad}")


def load_valid_interface_run(run: Path, supplied_sha: str) -> dict:
    """Load a run_petmad_interface.py output and refuse anything unfit for derived work values.

    Returns result, relaxation records, interface labels and the three saved final structures.
    """
    run = Path(run)
    try:
        result = json.loads((run / 'result.json').read_text())
        records = json.loads((run / 'relaxation_records.json').read_text())
    except (FileNotFoundError, json.JSONDecodeError) as error:
        raise ProvenanceError(f'{run}: missing or unreadable run record ({error})') from error
    require_matching_checkpoint(supplied_sha, {'result.json': result.get('checkpoint_sha256')})
    problems, failed = [], []   # integrity problems; genuine calculation failures
    for name in ('interface', 'film', 'substrate'):
        r = records.get(name)
        if r is None:
            problems.append(f'missing {name} relaxation record')
            continue
        if not (r.get('converged') and r.get('finite', True) and np.isfinite(r.get('final_energy_eV', np.nan))):
            failed.append(f'{name} relaxation is unconverged or non-finite')
        if r.get('overlap_violations'):
            failed.append(f'{name} has overlap violations')
        if result['relaxations'][name].get('final_energy_eV') != r.get('final_energy_eV'):
            problems.append(f'{name} energy differs between result.json and relaxation records')
    if not result.get('numerically_valid') and not failed:
        problems.append(f"run status {result.get('status')!r} is not numerically valid, but no relaxation failed")
    try:
        initial = read(run / 'initial.extxyz')
        finals = {name: read(run / name / 'final.extxyz') for name in ('interface', 'film', 'substrate')}
    except (FileNotFoundError, OSError, ValueError) as error:
        raise ProvenanceError(f'{run}: missing or unreadable structure ({error})') from error
    labels = np.asarray(initial.arrays.get('interface_label', []))
    if len(labels) != len(finals['interface']) or set(labels) != {'film', 'substrate'}:
        problems.append('interface labels missing or inconsistent with the joined structure')
    else:
        joined = finals['interface']
        for part in ('film', 'substrate'):
            idx = np.where(labels == part)[0]
            if joined[idx].get_chemical_symbols() != finals[part].get_chemical_symbols():
                problems.append(f'{part} fragment species/order differ from the saved {part} reference')
    cells = {name: atoms.cell.array for name, atoms in finals.items()}
    if not all(np.allclose(cells['interface'], c, atol=1e-6) for c in cells.values()):
        problems.append('joined and separated references do not share one cell')
    area = float(np.linalg.norm(np.cross(cells['interface'][0], cells['interface'][1])))
    if not np.isclose(area, result.get('area_A2', np.nan), rtol=1e-8):
        problems.append(f"area {area:.6f} Å² differs from recorded {result.get('area_A2')}")
    if problems:   # integrity dominates: a broken package is never reported as a chemistry outcome
        raise ProvenanceError(f'{run}: ' + '; '.join(problems + failed), kind='integrity')
    if failed:
        raise ProvenanceError(f'{run}: ' + '; '.join(failed), kind='calculation')
    return {'result': result, 'records': records, 'labels': labels, 'finals': finals, 'area_A2': area}
