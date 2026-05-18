"""Test 0259 — Python Reference 2.5.4.2: Escaped characters (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_4_2_a(x: int) -> int:
    """Variation A for Escaped characters."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_4_2_a(4) == 5
