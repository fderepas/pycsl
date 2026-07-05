"""Test 0814 — WL-02 regression lock (NEGATIVE twin of 0813). # pycsl-expected: FAIL

Guards the soundness fix from regressing. Before the fix PyCSL lowered Python `/`
(TRUE division) to the integer Euclidean `pycsl_div`, silently dropping the
fractional part and PROVING the FALSE `5 / 2 == 2` (CPython 5 / 2 == 2.5, and
`2.5 == 2` is False). With the faithful real lowering, `5 / 2` is a `real`; using
it at `int` type (`-> int`, `\result == 2`) is a real-vs-int type error and must
NOT be provable. If this test ever PASSES again, the WL-02 unsoundness has returned.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == 2
def truediv_int_trunc_UNSOUND() -> int:
    """True division yields the real 2.5; the `== 2` int claim is the old bug."""
    return 5 / 2


if __name__ == "__main__":
    assert truediv_int_trunc_UNSOUND() == 2.5  # CPython — proof of `== 2` must fail
