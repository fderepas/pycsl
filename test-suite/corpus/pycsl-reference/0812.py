"""Test 0812 — WL-01 regression lock (NEGATIVE twin of 0811). # pycsl-expected: FAIL

Guards the soundness fix from regressing. Before the fix PyCSL lowered Python `//`
to Why3 int.EuclideanDivision `div`, which PROVED the FALSE `(-7)//(-2) == 4`
(CPython = 3). This driver asserts that old Euclidean value; with floored lowering
it is FALSE of the real result (3) and must NOT be provable. If this test ever
PASSES again, the WL-01 unsoundness has returned.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 4
def floordiv_neg_neg_UNSOUND() -> int:
    """Real value is 3 (floor of 3.5); the `== 4` claim is the old Euclidean bug."""
    return (-7) // (-2)


if __name__ == "__main__":
    assert floordiv_neg_neg_UNSOUND() == 3  # CPython — proof of `== 4` must fail
