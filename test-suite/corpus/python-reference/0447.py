"""Test 0447 — Python Reference 6.3.2.4: Formal subscription grammar (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_3_2_4_a(x: int) -> int:
    """Variation A for Formal subscription grammar."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_3_2_4_a(4) == 5
