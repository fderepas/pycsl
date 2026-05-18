"""Test 0435 — Python Reference 6.2.10.1: Generator-iterator methods (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_2_10_1_a(x: int) -> int:
    """Variation A for Generator-iterator methods."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_2_10_1_a(4) == 5
