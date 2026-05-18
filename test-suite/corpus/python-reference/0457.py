"""Test 0457 — Python Reference 6.17: Operator precedence (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_17_a(x: int) -> int:
    """Variation A for Operator precedence."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_17_a(4) == 5
