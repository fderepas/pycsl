"""Test 0349 — `Optional[int]` return annotation.

Module5 extracts `Optional[T]` and unwraps to T (since PyCSL models
`None` as `0`, the Optional-ness adds no type-level info Module6 could
use). For `Optional[int]`, the annotation lands as `"int"`. The
function below therefore type-checks under full proof exactly as a
function declared `-> int` would.
"""
from typing import Optional

#@ requires x >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def maybe_double(x: int) -> Optional[int]:
    return x + x

if __name__ == "__main__":
    assert maybe_double(0) == 0
    assert maybe_double(7) == 14
    print("PASS")
