"""Test 0037 — Python Reference 2.7: Operators and delimiters"""
_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def test_operators_and_delimiters() -> int:
    """Ref 2.7: the arithmetic, shift and bitwise operators, each pinned by a contract
    instead of an `assert` (which Module 6 DROPS). Previously the whole body was
    `return 0` (relaunch #46, `bin/check-vacuous-drivers.py`)."""
    a = 7 + 3 - 2
    b = 4 * 3
    c = 13 // 4
    d = 13 % 4
    e = 2 ** 5
    f = 6 & 3
    g = 6 | 3
    h = 6 ^ 3
    i = 1 << 4
    j = 32 >> 2
    if a == 8 and b == 12 and c == 3 and d == 1 and e == 32:
        if f == 2 and g == 7 and h == 5 and i == 16 and j == 8:
            return 1
    return 0

if __name__ == "__main__":
    assert test_operators_and_delimiters() == 1
