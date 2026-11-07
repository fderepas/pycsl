"""Test 0987 — the sharper half of route #18: ALIASING an array local to a PARAMETER was a
no-op, so the model answered every later read from the old literal.

    #@ ensures \result == 1                       <-- FALSE OF THE PROGRAM
    def f(ys: List[int]) -> int:
        xs: List[int] = [1, 2]
        xs = ys
        return xs[0]

    [+] Verification SUCCESS! All contracts formally proven.

Real Python returns `ys[0]` — whatever the caller passed. There is no precondition on `ys`
at all, so the model proved a specific value for an arbitrary input.

Same refusal, same reason as 0986: the array-local representation (a fixed `Array.make`
plus a `<name>_len` counter) is not a rebindable reference.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f(ys: List[int]) -> int:
    xs: List[int] = [1, 2]
    xs = ys
    return xs[0]
