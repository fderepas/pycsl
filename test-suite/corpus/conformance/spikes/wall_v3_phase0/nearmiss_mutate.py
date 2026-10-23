# wall_v3_phase0_nearmiss_mutate.py — NEAR-MISS (recognizer must NOT fire).
# T-A generic-walk shape, but it mutates the iterated SUBJECT during iteration.
# Disqualifier: subject mutation during iteration (breaks the pure-inductive-value
# framing the template relies on; pattern-spec v1 rejects).
from typing import Any, Set


def collect_targets(obj: Any, targets: Set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            del obj[k]                     # <-- DISQUALIFIER: mutates the iterated subject
            collect_targets(v, targets)
    elif isinstance(obj, list):
        for item in obj:
            collect_targets(item, targets)
