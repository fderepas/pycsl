"""Test 0678 — negative: subscript-assign to a non-list/dict variable.

`_validate_subscript_assignments` (annotated functions only) rejects `n[i] = v` where
`n` is not list/dict-typed (here `int`): `Subscript assignment to non-list/dict variable
'n' (type 'int') in function 'f'`. Characterization test for the IR migration (Phase B).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
def f(n: int) -> int:
    n[0] = 5
    return 0
