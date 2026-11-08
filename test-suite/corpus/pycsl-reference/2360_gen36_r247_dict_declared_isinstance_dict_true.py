r"""Test 2360 — route #247 (expected PASS): CONTROL. A subject declared `Dict[int, int]` still decides
`isinstance(d, dict)` TRUE and `isinstance(d, set)` FALSE (distinct builtin tags; CPython `f({})` = 1).
"""
# pycsl-expected: PASS
from typing import Dict


#@ ensures \result == 1
#@ assigns \nothing
def f(d: Dict[int, int]) -> int:
    if isinstance(d, dict):
        if not isinstance(d, set):
            return 1
    return 0


if __name__ == "__main__":
    assert f({}) == 1
