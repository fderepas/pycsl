r"""Test 1729 — WITNESS for `PYCSL-SEM-FINAL` (F1), one of the 140 refusals that had none.

`bin/check-refusal-witness-coverage.py` joins the compiler's 198 `raise PyCSL*Error` sites
against a census of every expected-FAIL corpus witness and reports how many are
DEMONSTRATED to fire: 58 at the first measurement, 140 not. Route #209 is what that gap
costs — a trust boundary that read correctly, had been reviewed, and had never fired.

This file demonstrates F1: a bare-name write to a module-level `Final` is refused
("write-once at declaration; PEP 591"). Twin: 1730 covers F2, the `self.<attr>` write to a
`Final` instance attribute outside `__init__`.
"""
# pycsl-expected: FAIL
from typing import Final

_ = 0  # anchor

LIMIT: Final[int] = 10


#@ requires n >= 0
#@ ensures \result == 0
def f(n: int) -> int:
    global LIMIT
    LIMIT = 20
    return 0
