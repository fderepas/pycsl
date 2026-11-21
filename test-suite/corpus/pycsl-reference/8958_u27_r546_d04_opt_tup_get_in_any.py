r"""Test 8958 -- route #546 residual (control, expected PASS; u27 d04_opt_tup_get_in_any): `-> Optional[Tuple[Any, int]]` returning `(d.get('a'), k)` -- a may-be-None `.get` in the `Any` slot
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


#@ requires 0 <= k <= 1000
def g(k: int) -> Optional[Tuple[Any, int]]:
    d: Dict[str, int] = {}
    return (d.get('a'), k)


#@ requires 0 <= k <= 1000
#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    if t is not None:
        x = t[1]
        return x + 1
    return 0


if __name__ == "__main__":
    print("result", f(3))
