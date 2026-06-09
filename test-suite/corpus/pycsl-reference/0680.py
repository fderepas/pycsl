"""Test 0680 — negative: `\result` in a `#@ assert` checkpoint.

`_validate_checkpoints` rejects `\result` in a mid-body `#@ assert`/`#@ check` (it is
bound only at return). Context `function 'f'`. Characterization test for the IR
migration (Phase B / AST-only).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
def f() -> int:
    x = 0
    #@ assert \result == 0
    return x
