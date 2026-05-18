"""Test 0374 — Python Reference 4.2.1: Binding of names (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_4_2_1_b(x: int) -> int:
    """Variation B for Binding of names."""
    return x + x

if __name__ == "__main__":
    assert test_ref_4_2_1_b(3) == 6
