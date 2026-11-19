r"""Test 7854 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): g's three-argument `pow` with a parameter modulus (partial); f catches ValueError; CPython returns 2 (red team 44 probe g512/v51236_pow_mod_zero_h.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(n: int) -> int:
    y = pow(2, 3, n)
    return 1


#@ ensures \result == 1
def f(n: int) -> int:
    try:
        return g(n)
    except ValueError:
        return 2


if __name__ == "__main__":
    try:
        r = f(0)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
