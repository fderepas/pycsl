"""Test 0463 — Python Reference 7.3: The :keyword:`!assert` statement (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_7_3_a(x: int) -> int:
    """Variation A for The :keyword:`!assert` statement."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_7_3_a(4) == 5
