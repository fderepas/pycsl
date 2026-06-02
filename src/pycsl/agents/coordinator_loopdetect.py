"""Loop-detection helpers for the coordinator agent.

The coordinator halts with exit 73 (human-needed) when agent-reconcile proposes
the *same* recommendation three times in a row — a sign the automated fix loop
is stuck. This module holds the pure similarity/streak logic so it is
independently testable; `CoordinatorAgent` delegates to it.
"""
from __future__ import annotations

from typing import List, Tuple


def rec_key(rec: dict) -> Tuple[str, str]:
    """Normalised (target, recommendation-text) pair for similarity checks."""
    return (
        rec.get("target", "").strip().lower(),
        rec.get("recommendation", "").strip().lower(),
    )


def are_similar(rec1: dict, rec2: dict) -> bool:
    """Two recommendations are 'similar' iff they share a normalised key."""
    return rec_key(rec1) == rec_key(rec2)


def consecutive_similar(new_rec: dict, history: List[dict]) -> int:
    """Count how many tail entries of `history` are similar to `new_rec`."""
    count = 0
    for past in reversed(history):
        if are_similar(new_rec, past):
            count += 1
        else:
            break
    return count
