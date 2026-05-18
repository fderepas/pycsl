"""Test 0226 — PyCSL Annotation Reference 3.2.8 (div and mod combined)"""
_ = 0  # anchor
#@ requires x >= 0 and y > 0
#@ ensures \result == x // y + x % y
def test_div_mod(x: int, y: int) -> int:
    q = x // y
    r = x % y
    return q + r

if __name__ == "__main__":
    assert test_div_mod(10, 3) == 4
    assert test_div_mod(9, 3) == 3
