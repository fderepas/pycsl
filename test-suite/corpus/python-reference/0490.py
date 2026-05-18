"""Test 0490 — Python Reference 8.8.1: Multiple inheritance (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_8_8_1_b(x: int) -> int:
    """Variation B for Multiple inheritance."""
    return x + x

if __name__ == "__main__":
    assert test_ref_8_8_1_b(3) == 6
