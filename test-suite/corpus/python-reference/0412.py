"""Test 0412 — Python Reference 5.4.5: Module reprs (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_4_5_b(x: int) -> int:
    """Variation B for Module reprs."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_4_5_b(3) == 6
