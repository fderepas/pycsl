"""Test 0333 — Python Reference 3.2.13.6: Class method objects (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_13_6_a(x: int) -> int:
    """Variation A for Class method objects."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_13_6_a(4) == 5
