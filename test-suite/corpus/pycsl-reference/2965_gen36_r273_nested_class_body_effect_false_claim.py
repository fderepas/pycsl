r"""Test 2965 — route #273 (expected FAIL): the nested class body `v = push(xs)` runs at
the `class` statement and writes `xs[0] = 5`; `f` claims `\result == 0` for `return xs[0]`.
PROVED at 5a307a33. CPython: 5. Now refused (PYCSL-SEM-DEF-TIME-EVALUATION).
"""
# pycsl-expected: FAIL
from typing import List

#@ requires len(xs) >= 1
#@ ensures \result == 0
#@ assigns xs[0]
def push(xs: List[int]) -> int:
    xs[0] = 5
    return 0

#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
#@ assigns xs[0]
def f(xs: List[int]) -> int:
    class K:
        v = push(xs)
    return xs[0]

if __name__ == "__main__":
    print(f([0]))
