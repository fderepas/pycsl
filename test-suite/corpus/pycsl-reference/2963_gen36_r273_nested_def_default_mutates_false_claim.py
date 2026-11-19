r"""Test 2963 — route #273 (expected FAIL): the nested def's default `push(xs)` runs when
the `def` executes and writes `xs[0] = 5`; `f` claims `\result == 0` for `return xs[0]`.
The write vanished with the default: PROVED at 5a307a33. CPython: 5. Now refused
(PYCSL-SEM-DEF-TIME-EVALUATION).
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
    def inner(y: int = push(xs)) -> int:
        return y
    return xs[0]

if __name__ == "__main__":
    print(f([0]))
