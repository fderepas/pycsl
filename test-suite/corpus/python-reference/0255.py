"""Test 0255 — Python Reference 2.5.3: Formal grammar (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_3_a(x: int) -> int:
    """Variation A for Formal grammar."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_3_a(4) == 5
