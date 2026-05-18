"""Test 0476 — Python Reference 7.12: The :keyword:`!global` statement (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_7_12_b(x: int) -> int:
    """Variation B for The :keyword:`!global` statement."""
    return x + x

if __name__ == "__main__":
    assert test_ref_7_12_b(3) == 6
