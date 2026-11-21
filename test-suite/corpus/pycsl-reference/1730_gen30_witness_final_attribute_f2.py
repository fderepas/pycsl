r"""Test 1730 — WITNESS for `PYCSL-SEM-FINAL` (F2), the instance-attribute half.

A `self.<attr>` write to a `Final` instance attribute OUTSIDE `__init__` is refused
("__init__-only writes; PEP 591"). Its twin 1729 covers F1, the module-level name. Both
exist because `bin/check-refusal-witness-coverage.py` measured that 140 of the compiler's
198 refusal sites had no file proving they can fire.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from typing import Final

_ = 0  # anchor


class C:
    k: Final[int]

    def __init__(self) -> None:
        self.k = 1

    #@ ensures \result == 0
    def bump(self) -> int:
        self.k = 2
        return 0
