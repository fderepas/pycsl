"""Test 0342 — Python Reference 3.3.3.3: Determining the appropriate metaclass (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_3_3_b(x: int) -> int:
    """Variation B for Determining the appropriate metaclass."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_3_3_b(3) == 6
