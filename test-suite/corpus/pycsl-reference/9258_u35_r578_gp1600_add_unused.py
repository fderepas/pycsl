r"""Test 9258 -- route #578 (expected FAIL: PROVED at base `no_exception \all`, NOT PROVED: route #252's obligation at the operation on the arbitrary slot; red team 55 probe gp1600_add_unused.py): `t = g(k)`; `v = t[1] + 1`; `return 0`; CPython TypeError unsupported operand type(s) for +: 'NoneType' and 'int'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> Tuple[int, Any]:
    return (1, None)


#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    v = t[1] + 1
    return 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
