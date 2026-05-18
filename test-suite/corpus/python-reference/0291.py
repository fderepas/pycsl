"""Test 0291 — Python Reference 3.2.4.1: :class:`numbers.Integral` (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_4_1_a(x: int) -> int:
    """Variation A for :class:`numbers.Integral`."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_4_1_a(4) == 5
