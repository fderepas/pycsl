r"""Test 2986 — route #275 control (expected PASS): whatever the key, `sorted` returns a
permutation of the same length, so `len(ys) == 2` still proves. CPython: 2.
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    xs: List[int] = [1, 2]
    ys = sorted(xs, key=lambda v: -v)
    return len(ys)


if __name__ == "__main__":
    assert f() == 2
