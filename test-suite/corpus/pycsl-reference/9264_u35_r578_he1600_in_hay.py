r"""Test 9264 -- route #578 (expected FAIL: PROVED at base `no_exception \all`, NOT PROVED: route #252's obligation at the operation on the arbitrary slot; red team 55 probe he1600_in_hay.py): `t = g(k)`; `return 1 if k in t[1] else 0`; CPython TypeError argument of type 'NoneType' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(k: int) -> Tuple[int, Any]:
    return (1, None)


#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    return 1 if k in t[1] else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
