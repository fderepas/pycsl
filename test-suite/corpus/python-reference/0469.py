"""Test 0469 — Python Reference 7.6: The :keyword:`!return` statement (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_7_6_a(x: int) -> int:
    """Variation A for The :keyword:`!return` statement."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_7_6_a(4) == 5
