"""Test 0470 — Python Reference 7.6: The :keyword:`!return` statement (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_7_6_b(x: int) -> int:
    """Variation B for The :keyword:`!return` statement."""
    return x + x

if __name__ == "__main__":
    assert test_ref_7_6_b(3) == 6
