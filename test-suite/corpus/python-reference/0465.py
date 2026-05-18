"""Test 0465 — Python Reference 7.4: The :keyword:`!pass` statement (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_7_4_a(x: int) -> int:
    """Variation A for The :keyword:`!pass` statement."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_7_4_a(4) == 5
