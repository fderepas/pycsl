"""Test 0467 — Python Reference 7.5: The :keyword:`!del` statement (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_7_5_a(x: int) -> int:
    """Variation A for The :keyword:`!del` statement."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_7_5_a(4) == 5
