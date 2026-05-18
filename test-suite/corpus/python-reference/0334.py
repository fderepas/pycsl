"""Test 0334 — Python Reference 3.2.13.6: Class method objects (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_13_6_b(x: int) -> int:
    """Variation B for Class method objects."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_13_6_b(3) == 6
