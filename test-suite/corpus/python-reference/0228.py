"""Test 0228 — Python Reference 2.1.3: Comments (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_1_3_b(x: int) -> int:
    """Variation B for Comments."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_1_3_b(3) == 6
