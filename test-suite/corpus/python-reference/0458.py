"""Test 0458 — Python Reference 6.17: Operator precedence (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_17_b(x: int) -> int:
    """Variation B for Operator precedence."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_17_b(3) == 6
