r"""Test 1992 — gen #36 (expected FAIL, refused): ROUTE #233 — a capture of a CALL subject

Binding the capture repeats the subject expression; for a call that would evaluate it twice,
so the shape is refused fail-closed (route #233 diagnostic). The claim itself is true in
CPython (`f() == 3`); the refusal is what this witness pins.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return 3


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    match g():
        case y:
            return y
