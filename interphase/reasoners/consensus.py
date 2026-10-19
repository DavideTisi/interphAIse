"""Self-consistency by repeated sampling (HELLMM: enumerator ×3, pruner ×5).

The agreement fraction is logged with every decision; it is the per-decision
confidence the orchestrator and the benchmark report.
"""

from __future__ import annotations

import warnings
from collections import Counter
from typing import Callable, Hashable, TypeVar

T = TypeVar("T")


def sample(fn: Callable[[], T], n: int) -> list[T]:
    """Call ``fn`` n times, dropping failed calls (logged as warnings)."""
    out = []
    for i in range(n):
        try:
            out.append(fn())
        except Exception as e:  # malformed JSON, validation error, network
            warnings.warn(f"consensus sample {i + 1}/{n} failed: {e}")
    if not out:
        raise RuntimeError(f"all {n} consensus samples failed")
    return out


def majority(items: list[T], key: Callable[[T], Hashable]) -> tuple[T, float]:
    """Most common item by ``key``; returns (representative, agreement fraction)."""
    counts = Counter(key(x) for x in items)
    best_key, n = counts.most_common(1)[0]
    rep = next(x for x in items if key(x) == best_key)
    return rep, n / len(items)


def rank_by_votes(lists: list[list[T]], key: Callable[[T], Hashable], top: int) -> list[tuple[T, float]]:
    """Borda-style aggregation of ranked lists; returns (item, vote fraction)."""
    score: Counter = Counter()
    seen: dict = {}
    votes: Counter = Counter()
    for lst in lists:
        for rank, x in enumerate(lst):
            k = key(x)
            seen.setdefault(k, x)
            score[k] += len(lst) - rank
            votes[k] += 1
    ordered = sorted(score, key=lambda k: (-score[k], str(k)))[:top]
    return [(seen[k], votes[k] / len(lists)) for k in ordered]
