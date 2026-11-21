# wall_v3_phase0_nearmiss_nonself.py — NEAR-MISS (recognizer must NOT fire).
# Walk shape, but the recursion goes to a DIFFERENT function, not self.
# Disqualifier: non-self recursion — there is no structural sub-term relating the
# callee's argument to this function's measure, so the size-variant would not close;
# pattern-spec v1 requires self-recursion on the iterated value.
from typing import Any, Set


def _emit(obj: Any, targets: Set[str]) -> None:
    targets.add(str(obj))


def collect_targets(obj: Any, targets: Set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            _emit(v, targets)              # <-- DISQUALIFIER: not self-recursion
    elif isinstance(obj, list):
        for item in obj:
            _emit(item, targets)
