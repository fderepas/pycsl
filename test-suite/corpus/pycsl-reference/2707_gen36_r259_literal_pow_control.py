r"""Test 2707 — route #259 CONTROL (expected PASS): `2 ** 3` with literal non-negative
operands constant-folds to `8`; the exponent obligation never arises.
"""


#@ ensures \result == 8
#@ assigns \nothing
def f() -> int:
    return 2 ** 3


if __name__ == "__main__":
    assert f() == 8
