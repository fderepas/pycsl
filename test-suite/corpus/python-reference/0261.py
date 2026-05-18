"""Test 0261 — Python Reference 2.5.4.3: Octal character (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_5_4_3_a(x: int) -> int:
    """Variation A for Octal character."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_5_4_3_a(4) == 5
