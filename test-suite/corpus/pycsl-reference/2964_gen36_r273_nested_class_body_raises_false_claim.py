r"""Test 2964 — route #273 (expected FAIL): a nested class body runs when the `class`
statement executes; `v = 10 // x` with `x == 0` raises ZeroDivisionError under `f`'s
`no_exception \all`. The class body was dropped: PROVED at 5a307a33. CPython:
ZeroDivisionError. Now refused (PYCSL-SEM-DEF-TIME-EVALUATION).
"""
# pycsl-expected: FAIL

#@ requires x == 0
#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    class K:
        v = 10 // x
    return 1

if __name__ == "__main__":
    try:
        print(f(0))
    except ZeroDivisionError:
        print("ZeroDivisionError")
