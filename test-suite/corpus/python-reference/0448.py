"""Test 0448 — Python Reference 6.3.2.4: Formal subscription grammar (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_3_2_4_b(x: int) -> int:
    """Variation B for Formal subscription grammar."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_3_2_4_b(3) == 6
