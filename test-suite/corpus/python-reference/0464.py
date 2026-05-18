"""Test 0464 — Python Reference 7.3: The :keyword:`!assert` statement (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_7_3_b(x: int) -> int:
    """Variation B for The :keyword:`!assert` statement."""
    return x + x

if __name__ == "__main__":
    assert test_ref_7_3_b(3) == 6
