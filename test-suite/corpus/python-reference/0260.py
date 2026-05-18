"""Test 0260 — Python Reference 2.5.4.2: Escaped characters (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_4_2_b(x: int) -> int:
    """Variation B for Escaped characters."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_4_2_b(3) == 6
