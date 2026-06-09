"""Test 0674 — negative: unresolved quantifier binder type in a LOOP invariant.

`_validate_quant_binders` rejects `\forall x: Bogus` (an unresolved binder type). Inside
a `#@ loop invariant` the context is `while loop at line N inside function 'f'`. Surface
twin of 0556 (function). Characterization test for the B (quant_binders) IR migration.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


def f() -> int:
    i = 0
    #@ loop invariant \forall x: Bogus; x == x
    while i < 1:
        i = i + 1
    return 0
