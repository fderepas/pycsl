"""Test 0265 — Python Reference 2.5.4.5: Named Unicode character (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_4_5_a(x: int) -> int:
    """Variation A for Named Unicode character."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_4_5_a(4) == 5
