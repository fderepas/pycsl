r"""Test 8954 -- route #546 residual (control, expected PASS; u27 c08_union_tup_ints): `-> Union[Tuple[int, int], None]` returning `(k, k)`; the caller reads `x = t[0]; x + 1`
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass


#@ requires 0 <= k <= 1000
def g(k: int) -> Union[Tuple[int, int], None]:
    return (k, k)


#@ requires 0 <= k <= 1000
#@ no_exception \all
def f(k: int) -> int:
    t = g(k)
    if t is not None:
        x = t[0]
        return x + 1
    return 0


if __name__ == "__main__":
    print("result", f(3))
