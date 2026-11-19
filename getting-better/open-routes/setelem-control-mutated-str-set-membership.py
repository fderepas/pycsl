r"""CONTROL for `setelem-carrier-read-only-str-set-membership.py` — the SAME membership on a
MUTATED `Set[str]` parameter, which VERIFIES today.

This is the probe that turned a table of symptoms into a mechanism, and it was run as a
PREDICTION rather than as another symptom: if `_mut_coll` is what buys the string key, then a
parameter that is both `.add`ed to and tested must type-check. It does.

    #@ assigns held
    def f(held: Set[str], m: str) -> bool:
        held.add(m)
        return m in held          # VERIFIES

One type, two paths, and only the path that mutates carries the element type. Wall-lesson
(a6): explain by prediction, not by re-reading.

IF THIS FILE EVER FAILS, the `_mut_coll` branch has been lost and the carrier's diagnosis is
wrong.
"""
_ = 0  # anchor
from typing import Set


#@ ensures \result == 1
#@ assigns held
def add_then_test(held: Set[str], m: str) -> int:
    held.add(m)
    if m in held:
        return 1
    return 0
