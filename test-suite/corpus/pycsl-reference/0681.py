"""Test 0681 — negative: `\result` in a `#@ check` checkpoint (inside a loop).

`_validate_checkpoints` rejects `\result` in a `#@ check`; the body walk must find it
nested in a loop. Context `function 'f'` (uniform — no surface tracking). Twin of 0680.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 0
def f() -> int:
    i = 0
    while i < 1:
        #@ check \result == 0
        i = i + 1
    return 0
