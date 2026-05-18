"""Test 0230 — Python Reference 2.1.4: Encoding declarations (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_1_4_b(x: int) -> int:
    """Variation B for Encoding declarations."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_1_4_b(3) == 6
