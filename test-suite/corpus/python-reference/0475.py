"""Test 0475 — Python Reference 7.12: The :keyword:`!global` statement (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_7_12_a(x: int) -> int:
    """Variation A for The :keyword:`!global` statement."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_7_12_a(4) == 5
