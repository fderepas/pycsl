"""Test 0495 — Python Reference 8.9.3: The :keyword:`!async with` statement (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_8_9_3_a(x: int) -> int:
    """Variation A for The :keyword:`!async with` statement."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_8_9_3_a(4) == 5
