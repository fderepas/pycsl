r"""Test 3452 -- route #295 (expected FAIL): `e = iddh(d); e[1] = 2` with an IMPORTED `iddh` PROVED `\result == 1`; CPython: 2. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import Dict, Set, List
from multi_file_lib.r295_idd import iddh

#@ ensures \result == 1
def f(c: int) -> int:
    d: Dict[int, int] = {1: 1}
    e: Dict[int, int] = iddh(d)
    e[1] = 2
    return d[1]

if __name__ == "__main__":
    assert f(1) == 2, f(1)
