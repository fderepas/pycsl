"""Test 0350 — `Union[int, None]` return annotation.

Module5 extracts `Union[T1, T2]` by picking the first non-`None`
component. For `Union[int, None]` the annotation lands as `"int"` —
equivalent to `Optional[int]` from PyCSL's perspective. The function
below therefore type-checks under full proof exactly as a function
declared `-> int` would.
"""
from typing import Union

#@ requires x >= 1
#@ ensures \result >= 1
#@ assigns \nothing
def maybe_succ(x: int) -> Union[int, None]:
    return x + 1

if __name__ == "__main__":
    assert maybe_succ(1) == 2
    assert maybe_succ(10) == 11
    print("PASS")
