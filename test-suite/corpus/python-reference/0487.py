"""Test 0487 — Python Reference 8.5: The :keyword:`!with` statement (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_8_5_a(x: int) -> int:
    """Variation A for The :keyword:`!with` statement."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_8_5_a(4) == 5
