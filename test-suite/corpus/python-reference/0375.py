"""Test 0375 — Python Reference 4.2.2: Resolution of names (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_4_2_2_a(x: int) -> int:
    """Variation A for Resolution of names."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_4_2_2_a(4) == 5
