"""Test 0344 — Python Reference 3.3.3.4: Preparing the class namespace (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_3_4_b(x: int) -> int:
    """Variation B for Preparing the class namespace."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_3_4_b(3) == 6
