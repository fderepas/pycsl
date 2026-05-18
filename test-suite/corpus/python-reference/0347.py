"""Test 0347 — Python Reference 3.3.3.6: Creating the class object (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_3_6_a(x: int) -> int:
    """Variation A for Creating the class object."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_3_6_a(4) == 5
