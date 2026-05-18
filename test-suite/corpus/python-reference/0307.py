"""Test 0307 — Python Reference 3.2.8.9: Class Instances (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_8_9_a(x: int) -> int:
    """Variation A for Class Instances."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_8_9_a(4) == 5
