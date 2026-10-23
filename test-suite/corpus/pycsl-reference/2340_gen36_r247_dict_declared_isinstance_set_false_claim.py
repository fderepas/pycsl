r"""Test 2340 — route #247 (expected FAIL): `set` shared `dict`'s type tag, so a subject DECLARED
`Dict[int, int]` decided `isinstance(d, set)` TRUE (`(4 = 4)`) and `\result == 1` PROVED at afe28c69.
CPython `f({})` = 0. `set` now has its own tag: `(4 = 7)`.
"""
# pycsl-expected: FAIL
from typing import Dict


#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[int, int]) -> int:
    if isinstance(d, set):
        return 1
    return 0


if __name__ == "__main__":
    assert f({}) == 0
