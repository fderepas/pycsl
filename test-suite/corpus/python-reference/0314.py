"""Test 0314 — Python Reference 3.2.11.1: Special attributes (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_11_1_b(x: int) -> int:
    """Variation B for Special attributes."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_11_1_b(3) == 6
