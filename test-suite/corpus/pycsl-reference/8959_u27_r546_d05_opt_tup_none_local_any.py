r"""Test 8959 -- route #546 residual (control, expected PASS; u27 d05_opt_tup_none_local_any): `-> Optional[Tuple[Any, int]]` returning `(v, k)` with `v = None` -- the None-bound local in the `Any` slot
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


#@ requires 0 <= k <= 1000
def g(k: int) -> Optional[Tuple[Any, int]]:
    v = None
    return (v, k)


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
