"""Test 0313 — Python Reference 3.2.11.1: Special attributes (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_11_1_a(x: int) -> int:
    """Variation A for Special attributes."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_11_1_a(4) == 5
