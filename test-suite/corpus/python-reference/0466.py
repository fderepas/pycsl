"""Test 0466 — Python Reference 7.4: The :keyword:`!pass` statement (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_7_4_b(x: int) -> int:
    """Variation B for The :keyword:`!pass` statement."""
    return x + x

if __name__ == "__main__":
    assert test_ref_7_4_b(3) == 6
