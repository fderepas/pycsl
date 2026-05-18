"""Test 0256 — Python Reference 2.5.3: Formal grammar (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_3_b(x: int) -> int:
    """Variation B for Formal grammar."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_3_b(3) == 6
