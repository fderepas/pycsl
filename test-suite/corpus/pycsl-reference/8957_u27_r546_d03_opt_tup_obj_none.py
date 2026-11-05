r"""Test 8957 -- route #546 residual (control, expected PASS; u27 d03_opt_tup_obj_none): `-> Optional[Tuple[object, int]]` returning `(None, k)`; the caller reads `x = t[1]; x + 1`
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


#@ requires 0 <= k <= 1000
def g(k: int) -> Optional[Tuple[object, int]]:
    return (None, k)


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
