"""Test 0266 — Python Reference 2.5.4.5: Named Unicode character (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_4_5_b(x: int) -> int:
    """Variation B for Named Unicode character."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_4_5_b(3) == 6
