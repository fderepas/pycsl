"""Test 0229 — Python Reference 2.1.4: Encoding declarations (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_1_4_a(x: int) -> int:
    """Variation A for Encoding declarations."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_1_4_a(4) == 5
