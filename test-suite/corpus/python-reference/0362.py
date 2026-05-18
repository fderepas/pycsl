"""Test 0362 — Python Reference 3.3.12: Annotations (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_12_b(x: int) -> int:
    """Variation B for Annotations."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_12_b(3) == 6
