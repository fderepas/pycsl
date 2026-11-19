r"""Test 8955 -- route #546 residual (control, expected PASS; u27 d01_opt_tup3_none_slot0): `-> Optional[Tuple[Any, int, int]]` returning `(None, k, k)`; the caller reads `x = t[2]; x + 1`
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


#@ requires 0 <= k <= 1000
def g(k: int) -> Optional[Tuple[Any, int, int]]:
    return (None, k, k)


#@ requires 0 <= k <= 1000
#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    if t is not None:
        x = t[2]
        return x + 1
    return 0


if __name__ == "__main__":
    print("result", f(3))
