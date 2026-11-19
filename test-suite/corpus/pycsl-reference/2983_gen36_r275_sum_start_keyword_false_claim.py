r"""Test 2983 — route #275 (expected FAIL): the generic builtin path DROPS keywords, so
`sum(xs, start=10)` was modelled as `sum(xs)` and `\result == 3` PROVED. CPython: 13. Now a
builtin keyword that no lowering reads is refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2]
    return sum(xs, start=10)


if __name__ == "__main__":
    assert f() == 13
