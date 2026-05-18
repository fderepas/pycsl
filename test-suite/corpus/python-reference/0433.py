"""Test 0433 — Python Reference 6.2.3.2: String literal concatenation (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_2_3_2_a(x: int) -> int:
    """Variation A for String literal concatenation."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_2_3_2_a(4) == 5
