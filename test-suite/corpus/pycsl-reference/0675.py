"""Test 0675 — negative: unresolved quantifier binder type in a GHOST expression.

`_validate_quant_binders` rejects `\forall x: Bogus` in a `#@ ghost` value — context
`function 'f' (ghost 'g')`. Third surface twin of 0556. Characterization test for the
quant_binders IR migration.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


def f() -> int:
    #@ ghost g = \forall x: Bogus; x == x
    return 0
