"""Test 0308 — Python Reference 3.2.8.9: Class Instances (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_8_9_b(x: int) -> int:
    """Variation B for Class Instances."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_8_9_b(3) == 6
