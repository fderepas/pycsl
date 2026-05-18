"""Test 0343 — Python Reference 3.3.3.4: Preparing the class namespace (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_3_4_a(x: int) -> int:
    """Variation A for Preparing the class namespace."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_3_4_a(4) == 5
