r"""Test 8790 -- route #556 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R556-BUILTIN-OBJECT-OPERAND; red team 53 probe g1415/dp1202_F1_unclaimed_callee.py): an unclaimed callee `g` returns `1 if k in len else 0`; CPython TypeError: argument of type 'builtin_function_or_method' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> int:
    return 1 if k in len else 0


#@ no_exception \all
def f(k: int) -> int:
    return g(k) + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
