"""Test 0502 — Python Reference 8.11: Annotations (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_8_11_b(x: int) -> int:
    """Variation B for Annotations."""
    return x + x

if __name__ == "__main__":
    assert test_ref_8_11_b(3) == 6
