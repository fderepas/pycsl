"""Test 0376 — Python Reference 4.2.2: Resolution of names (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_4_2_2_b(x: int) -> int:
    """Variation B for Resolution of names."""
    return x + x

if __name__ == "__main__":
    assert test_ref_4_2_2_b(3) == 6
