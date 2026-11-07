# wall_v3_phase0_nearmiss_break.py — NEAR-MISS (recognizer must NOT fire).
# T-A generic-walk shape, but with an early `break` out of the walk loop.
# Disqualifier: early break/return from inside the loop (pattern-spec v1 rejects).
from typing import Any, Set


def collect_targets(obj: Any, targets: Set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "stop":
                break                      # <-- DISQUALIFIER: early break from the walk loop
            collect_targets(v, targets)
    elif isinstance(obj, list):
        for item in obj:
            collect_targets(item, targets)
