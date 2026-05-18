"""Test 0478 — Python Reference 7.14: The :keyword:`!type` statement (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_7_14_b(x: int) -> int:
    """Variation B for The :keyword:`!type` statement."""
    return x + x

if __name__ == "__main__":
    assert test_ref_7_14_b(3) == 6
