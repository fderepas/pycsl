"""Test 0811 — WL-01 regression lock (POSITIVE): Python `//` is FLOORED division
and `%` has the sign of the DIVISOR. PyCSL now lowers both to floored `pycsl_div`/
`pycsl_mod` (Euclidean corrected by a sign-of-divisor adjustment), so the faithful
CPython values are PROVABLE — including the previously-unsound negative-divisor case.

Ground truth (CPython):
  (-7) // (-2) == 3     7 % (-2) == -1     (negative divisor: floor / divisor-sign)
  (-7) // 2   == -4     7 % 2    == 1      (positive divisor: agrees with Euclidean)
  7 // 2      == 3      (-7) % (-2) == -1

Twin: 0812 (# pycsl-expected: FAIL) asserts the OLD false Euclidean `== 4`.
"""
_ = 0  # anchor


#@ ensures \result == 3
def floordiv_neg_neg() -> int:
    return (-7) // (-2)


#@ ensures \result == -1
def mod_pos_neg() -> int:
    return 7 % (-2)


#@ ensures \result == -4
def floordiv_neg_pos() -> int:
    return (-7) // 2


#@ ensures \result == 3
def floordiv_pos_pos() -> int:
    return 7 // 2


#@ ensures \result == 1
def mod_pos_pos() -> int:
    return 7 % 2


#@ ensures \result == -1
def mod_neg_neg() -> int:
    return (-7) % (-2)


#@ requires b != 0
#@ ensures \result == a // b
def floordiv_general(a: int, b: int) -> int:
    """The floored identity holds for a symbolic (possibly negative) divisor."""
    return a // b


if __name__ == "__main__":
    assert floordiv_neg_neg() == 3
    assert mod_pos_neg() == -1
    assert floordiv_neg_pos() == -4
    assert floordiv_pos_pos() == 3
    assert mod_pos_pos() == 1
    assert mod_neg_neg() == -1
    assert floordiv_general(-7, -2) == 3
    assert floordiv_general(7, -2) == -4
