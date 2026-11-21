r"""Test 7655 -- route #482 CONTROL (expected PASS: PROVED at base and candidate): a `\trusted` def with no `assigns` only reads its dict parameter (`k in d`, `d[k]`), so the caller keeps `d[1]`.
"""
# pycsl-expected: PASS
from typing import Dict


#@ \trusted
def k(d: Dict[int, int]) -> int:
    if 1 in d:
        return d[1] + 1
    return 0


#@ requires 1 in d and d[1] == 0
#@ ensures \result == 0
def f(d: Dict[int, int]) -> int:
    k(d)
    return d[1]


if __name__ == "__main__":
    print("result", f({1: 0}), "expected 0")
