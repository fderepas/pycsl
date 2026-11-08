r"""Test 3085 — route #279 (expected FAIL): a two-step alias `b = a; c = b; c += [2]` — the alias class
is closed over name-to-name assignments; `len(a) == 1` PROVED at 72ab1c57. CPython: 2. Now refused.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: List[int] = [1]
    b: List[int] = a
    c: List[int] = b
    c += [2]
    return len(a)


if __name__ == "__main__":
    assert f() == 2
