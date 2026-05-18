"""Test 0281 — Python Reference 2.6.1: Integer literals (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_6_1_a(x: int) -> int:
    """Variation A for Integer literals."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_6_1_a(4) == 5
