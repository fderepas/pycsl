"""Test 0679 — negative: subscript-assign to an undefined variable.

`_validate_subscript_assignments` rejects `nope[i] = v` where `nope` is not in scope:
`Subscript assignment to undefined variable 'nope' in function 'f'`. Characterization
test for the IR migration (Phase B).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
def f() -> int:
    nope[0] = 5
    return 0
