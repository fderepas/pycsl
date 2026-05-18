"""Test 0282 — Python Reference 2.6.1: Integer literals (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_6_1_b(x: int) -> int:
    """Variation B for Integer literals."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_6_1_b(3) == 6
