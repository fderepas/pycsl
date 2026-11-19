r"""Test 2716 — route #262 (expected FAIL): a LOOP INVARIANT is a contract too —
`xs[k] == 0` with `k == -1` read the raw cell `-1`, which the loop's stores never touch.
CPython: after the last iteration xs[-1] == 5, so the invariant is false.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires len(xs) == 3 and k == -1
#@ requires xs[2] == 0 and xs[k] == 0
#@ ensures \result == 0
#@ assigns xs[0], xs[1], xs[2]
def f(xs: List[int], k: int) -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= 3
    #@ loop invariant xs[k] == 0
    #@ loop variant 3 - i
    while i < 3:
        xs[i] = 5
        i = i + 1
    return 0


if __name__ == "__main__":
    xs = [0, 0, 0]
    f(xs, -1)
    assert xs[-1] == 5
