"""Test 1199 — ROUTE #78's CONTROL: the EMPTY `deque()` is FAITHFUL and must KEEP PROVING.

This is the file that stops route #78's repair from becoming an over-refusal. `deque()` with
no arguments genuinely IS the empty list, so the existing lowering to an empty `ArrayLit` is
correct for it; only the SEEDED form (1198) is refused. It plays exactly the role `@dataclass`
played for route #76 and the empty-slice control played for #17: a positive control that
fails loudly if the guard is ever widened to the whole construct.

If this file ever starts FAILING, route #78's guard has been widened past the seeded form and
the fix is to narrow it back, NOT to retire this test.
"""
from collections import deque
from typing import List


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    dq: List[int] = deque()
    dq.append(7)
    dq.append(8)
    return len(dq)
