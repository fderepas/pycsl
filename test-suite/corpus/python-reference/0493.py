"""Test 0493 — Python Reference 8.9.2: The :keyword:`!async for` statement (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_8_9_2_a(x: int) -> int:
    """Variation A for The :keyword:`!async for` statement."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_8_9_2_a(4) == 5
