"""Test 0496 — Python Reference 8.9.3: The :keyword:`!async with` statement (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_8_9_3_b(x: int) -> int:
    """Variation B for The :keyword:`!async with` statement."""
    return x + x

if __name__ == "__main__":
    assert test_ref_8_9_3_b(3) == 6
