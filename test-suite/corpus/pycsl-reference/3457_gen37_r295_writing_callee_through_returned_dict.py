r"""Test 3457 -- route #295 (expected FAIL): the alias handed to a WRITING callee `setk(e)` (`assigns x`) PROVED `\result == 1`; CPython: 2. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict, Set, List

#@ assigns \nothing
#@ \trusted
def idd(x: Dict[int, int]) -> Dict[int, int]:
    return x

#@ assigns x
def setk(x: Dict[int, int]) -> None:
    x[1] = 2

#@ ensures \result == 1
def f(c: int) -> int:
    d: Dict[int, int] = {1: 1}
    e = idd(d)
    setk(e)
    return d[1]

if __name__ == "__main__":
    assert f(1) == 2, f(1)
