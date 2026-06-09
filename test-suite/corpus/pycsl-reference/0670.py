"""Test 0670 — negative: `\valid` base must be a list/bytes parameter.

`_validate_predicate_bases` rejects `\valid` on a non-list/bytes base (here an `int`):
`\valid base 'n' is not a list/bytes parameter in function 'f' (got type 'int')`.
Characterization test for the B4 IR migration of this branch.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires \valid(n, 2)
def f(n: int) -> int:
    return 0
