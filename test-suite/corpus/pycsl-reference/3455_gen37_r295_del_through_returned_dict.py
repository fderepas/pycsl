r"""Test 3455 -- route #295 (expected FAIL): `del e[1]` through the returned alias PROVED `1 in d`; CPython: False. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict, Set, List

#@ assigns \nothing
#@ \trusted
def idd(x: Dict[int, int]) -> Dict[int, int]:
    return x

#@ ensures \result == 1
def f(c: int) -> int:
    d: Dict[int, int] = {1: 1, 2: 2}
    e = idd(d)
    del e[1]
    return 1 if 1 in d else 0

if __name__ == "__main__":
    assert f(1) == 0, f(1)
