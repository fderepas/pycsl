"""Test 0477 — Python Reference 7.14: The :keyword:`!type` statement (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_7_14_a(x: int) -> int:
    """Variation A for The :keyword:`!type` statement."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_7_14_a(4) == 5
