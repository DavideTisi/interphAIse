"""Run directory and decision log.

Every LLM decision and every deterministic gate result is appended to the
decision log with its inputs. The log is the audit trail ("why does this
interface model look like this?") and the input to benchmark/score_agreement.py.
"""

from __future__ import annotations

import dataclasses
import datetime as _dt
import json
import os
from pathlib import Path

import numpy as np


def _default(o):
    if dataclasses.is_dataclass(o):
        return dataclasses.asdict(o)
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, tuple)):
        return list(o)
    return str(o)


class RunLog:
    def __init__(self, case_name: str, root: str | os.PathLike | None = None):
        root = Path(root or os.environ.get("INTERPHAISE_RUN_DIR", "runs"))
        stamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = case_name.replace("|", "__").replace("@", "_at_").replace("/", "-")
        self.dir = root / f"{stamp}_{safe}"
        self.dir.mkdir(parents=True, exist_ok=True)
        self.case = case_name
        self.events: list[dict] = []

    def record(self, stage: str, kind: str, payload, **inputs) -> None:
        """kind: 'decision' | 'gate' | 'compute' | 'transition' | 'error'.

        'decision' events carry inputs.policy = 'llm' | 'rules' | 'human'.
        """
        self.events.append(
            {
                "t": _dt.datetime.now().isoformat(timespec="seconds"),
                "stage": stage,
                "kind": kind,
                "inputs": inputs,
                "output": payload,
            }
        )
        self.save()

    def decisions(self, stage: str | None = None) -> list[dict]:
        return [e for e in self.events if e["kind"] in ("decision", "llm_decision")
                and (stage is None or e["stage"] == stage)]

    def save(self) -> Path:
        path = self.dir / "decision_log.json"
        path.write_text(json.dumps({"case": self.case, "events": self.events}, indent=2, default=_default))
        return path
