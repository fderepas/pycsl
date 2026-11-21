r"""Test 9260 -- route #578 (expected FAIL: PROVED at base `no_exception \all`, NOT PROVED: route #252's obligation at the operation on the arbitrary slot; red team 55 probe gk1614_fix0_lt.py): `t = g(k)`; `return 1 if t[0] < k else 0`; CPython TypeError '<' not supported between instances of 'NoneType' and 'int'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> Tuple[Any, int]:
    return (None, 1)


#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    return 1 if t[0] < k else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
