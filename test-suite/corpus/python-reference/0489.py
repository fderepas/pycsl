"""Test 0489 — Python Reference 8.8.1: Multiple inheritance (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_8_8_1_a(x: int) -> int:
    """Variation A for Multiple inheritance."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_8_8_1_a(4) == 5
