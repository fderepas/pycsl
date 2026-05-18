"""Test 0431 — Python Reference 6.2.3.1: Literals and object identity (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_2_3_1_a(x: int) -> int:
    """Variation A for Literals and object identity."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_2_3_1_a(4) == 5
