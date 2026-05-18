"""Test 0468 — Python Reference 7.5: The :keyword:`!del` statement (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_7_5_b(x: int) -> int:
    """Variation B for The :keyword:`!del` statement."""
    return x + x

if __name__ == "__main__":
    assert test_ref_7_5_b(3) == 6
