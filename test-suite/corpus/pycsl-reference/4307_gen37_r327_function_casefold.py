r"""Test 4307 -- gen #37 route #327 (expected FAIL): two functions `F` and `f` emit two `let function f` (the later shadows the earlier). Fail-closed at base (Why3 / proof FAIL); REFUSED now.
"""
# pycsl-expected: FAIL
#@ ensures \result == 1
#@ assigns \nothing
def F() -> int:
    return 1
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return 2
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert g() == 1, g()
