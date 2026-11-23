r"""Test 10360 -- run #9 u65, route #619 (expected FAIL): red team rt75 F1 (probe c12). `f` and `g` are mutually recursive, so they are emitted as ONE `let rec ... with ...` group, and `f` (whose `requires` is contradictory: n >= 0 and n < 0) is the group's SECOND member, `with function f`. The non-vacuity gate's header scan matched only `^  let`, so the second member was never probed and the vacuous claim `\result == 99` was reported Verification SUCCESS (base b1400b11c). CPython: f(0) returns 1, VIOLATION of the claim. Now every member of a program `let rec` group is probed: FAILED (vacuous `f`).
"""
# pycsl-expected: FAIL


#@ requires n >= 0 and n < 0
#@ ensures \result == 99
#@ \variant n
#@ assigns \nothing
def f(n: int) -> int:
    if n == 0:
        return 1
    return g(n - 1)


#@ requires n >= 0
#@ ensures \result >= 0
#@ \variant n
#@ assigns \nothing
def g(n: int) -> int:
    if n == 0:
        return 0
    if n < 0 and n > 0:
        return f(n)
    return 0


if __name__ == "__main__":
    r = f(0)
    print("VIOLATION contract" if r != 99 else "result", r)
