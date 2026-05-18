"""Test 0348 — Python Reference 3.3.3.6: Creating the class object (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_3_6_b(x: int) -> int:
    """Variation B for Creating the class object."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_3_6_b(3) == 6
