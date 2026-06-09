"""Test 0671 — negative: `\separated` bases must be list/bytes parameters.

`_validate_predicate_bases` rejects `\separated` on non-list/bytes bases (here ints):
`\separated base 'a' is not a list/bytes parameter in function 'f' (got type 'int')`.
Characterization test for the B4 IR migration of this branch.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires \separated(a, 2, b, 2)
def f(a: int, b: int) -> int:
    return 0
