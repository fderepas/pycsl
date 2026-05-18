"""Test 0364 — Python Reference 3.3.13: Special method lookup (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_13_b(x: int) -> int:
    """Variation B for Special method lookup."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_13_b(3) == 6
