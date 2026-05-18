"""Test 0373 — Python Reference 4.2.1: Binding of names (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_4_2_1_a(x: int) -> int:
    """Variation A for Binding of names."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_4_2_1_a(4) == 5
