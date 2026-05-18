"""Test 0250 — Python Reference 2.4: Literals (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_4_b(x: int) -> int:
    """Variation B for Literals."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_4_b(3) == 6
