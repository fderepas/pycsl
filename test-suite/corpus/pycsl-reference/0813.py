"""Test 0813 — WL-02 regression lock (POSITIVE): Python `/` is TRUE division and
ALWAYS returns a float. PyCSL now lowers a body/contract `/` to a REAL division
(`from_int a /. from_int b` over Why3 real.RealInfix / real.FromInt), so the
faithful CPython value is PROVABLE at `float` (real) type — the fractional part is
preserved, never truncated.

Ground truth (CPython):
  5 / 2 == 2.5      1 / 2 == 0.5      7 / 2 == 3.5      4 / 2 == 2.0
  -5 / 2 == -2.5    (true division; the result is a float even for exact quotients)

Guard vs WL-01: `//` FLOOR division stays INTEGER (2 for 5//2), so the two operators
are NOT conflated. Twin: 0814 (# pycsl-expected: FAIL) asserts the OLD unsound
integer-truncation `5 / 2 == 2` at int type, which is now a real-vs-int type error.
"""
_ = 0  # anchor


#@ ensures \result == 2.5
def truediv_5_2() -> float:
    return 5 / 2


#@ ensures \result == 0.5
def truediv_1_2() -> float:
    return 1 / 2


#@ ensures \result == 3.5
def truediv_7_2() -> float:
    return 7 / 2


#@ ensures \result == 2.0
def truediv_exact_4_2() -> float:
    """Exact quotient is STILL a float (2.0), not an int."""
    return 4 / 2


#@ ensures \result == 2
def floordiv_5_2_stays_int() -> int:
    """WL-01 guard: `//` is FLOOR division and stays an integer (5 // 2 == 2)."""
    return 5 // 2


if __name__ == "__main__":
    assert truediv_5_2() == 2.5
    assert truediv_1_2() == 0.5
    assert truediv_7_2() == 3.5
    assert truediv_exact_4_2() == 2.0
    assert floordiv_5_2_stays_int() == 2
    # the two operators genuinely differ:
    assert (5 / 2) != (5 // 2)  # 2.5 != 2
