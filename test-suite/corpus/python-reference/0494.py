"""Test 0494 — Python Reference 8.9.2: The :keyword:`!async for` statement (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_8_9_2_b(x: int) -> int:
    """Variation B for The :keyword:`!async for` statement."""
    return x + x

if __name__ == "__main__":
    assert test_ref_8_9_2_b(3) == 6
