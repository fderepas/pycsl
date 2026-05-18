"""Test 0432 — Python Reference 6.2.3.1: Literals and object identity (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_2_3_1_b(x: int) -> int:
    """Variation B for Literals and object identity."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_2_3_1_b(3) == 6
