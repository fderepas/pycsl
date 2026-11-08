r"""Test 2960 — route #273 (expected FAIL): the nested def's default `10 // x` is evaluated
when the `def` statement runs inside `f`; with `x == 0` it raises ZeroDivisionError, yet
`f` claims `no_exception \all`. Module 5 lifts `inner` and drops the default, so the claim
PROVED at 5a307a33. CPython: ZeroDivisionError. Now refused
(PYCSL-SEM-DEF-TIME-EVALUATION).
"""
# pycsl-expected: FAIL

#@ requires x == 0
#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    def inner(y: int = 10 // x) -> int:
        return y
    return 1

if __name__ == "__main__":
    try:
        print(f(0))
    except ZeroDivisionError:
        print("ZeroDivisionError")
