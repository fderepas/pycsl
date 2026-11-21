r"""Test 2976 — route #274 (expected FAIL): a collection MUTATOR called on a receiver inside
a comprehension, `[out.append(y) for y in xs]`, appends to `out`; the opaque lowering dropped
it and `\result == 0` for `return len(out)` PROVED at 5a307a33. CPython: 1. Now refused
(PYCSL-SEM-VANISHED-CALL-EFFECT).
"""
# pycsl-expected: FAIL
from typing import List

#@ requires len(out) == 0
#@ ensures \result == 0
#@ assigns out
def f(out: List[int]) -> int:
    xs: List[int] = [1]
    ys = [out.append(y) for y in xs]
    return len(out)

if __name__ == "__main__":
    print(f([]))
