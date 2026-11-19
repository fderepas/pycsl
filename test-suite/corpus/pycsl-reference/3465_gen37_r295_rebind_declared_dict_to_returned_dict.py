r"""Test 3465 -- route #295 (expected FAIL): a REBIND of a declared dict `e = {}; e = idd(d); e[1] = 2` PROVED `\result == 1`; CPython: 2. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict, Tuple

#@ \trusted
#@ assigns \nothing
def idd(x: Dict[int, int]) -> Dict[int, int]:
    return x

#@ ensures \result == 1
def f() -> int:
    d: Dict[int, int] = {1: 1}
    e: Dict[int, int] = {}
    e = idd(d)
    e[1] = 2
    return d[1]

if __name__ == "__main__":
    assert f() == 2
