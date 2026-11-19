r"""Test 8641 -- route #546 (control, expected PASS): `-> Tuple[Optional[int], int]` returning `(None, k)` and `(k, k)` -- the None is in the Optional slot; the caller unpacks `a, b = g(k)` and reads `b + 1`
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires 0 <= k <= 1000
def g(k: int) -> Tuple[Optional[int], int]:
    if k > 5:
        return (None, k)
    return (k, k)


#@ requires 0 <= k <= 1000
#@ no_exception \all
def f(k: int) -> int:
    a, b = g(k)
    return b + 1


if __name__ == "__main__":
    print("result", f(3), f(7))
