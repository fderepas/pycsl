"""Test 0400 — Python Reference 5.3.3: Import hooks (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_3_3_b(x: int) -> int:
    """Variation B for Import hooks."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_3_3_b(3) == 6
