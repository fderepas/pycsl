"""Test 0436 — Python Reference 6.2.10.1: Generator-iterator methods (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_2_10_1_b(x: int) -> int:
    """Variation B for Generator-iterator methods."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_2_10_1_b(3) == 6
