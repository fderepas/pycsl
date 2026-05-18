"""Test 0292 — Python Reference 3.2.4.1: :class:`numbers.Integral` (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_4_1_b(x: int) -> int:
    """Variation B for :class:`numbers.Integral`."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_4_1_b(3) == 6
