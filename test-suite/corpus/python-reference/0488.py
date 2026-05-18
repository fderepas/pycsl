"""Test 0488 — Python Reference 8.5: The :keyword:`!with` statement (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_8_5_b(x: int) -> int:
    """Variation B for The :keyword:`!with` statement."""
    return x + x

if __name__ == "__main__":
    assert test_ref_8_5_b(3) == 6
