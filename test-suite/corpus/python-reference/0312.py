"""Test 0312 — Python Reference 3.2.10.2: Special methods (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_10_2_b(x: int) -> int:
    """Variation B for Special methods."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_10_2_b(3) == 6
