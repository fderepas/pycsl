"""Test 0510 — Python Reference 10.1: Full Grammar specification (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_10_1_b(x: int) -> int:
    """Variation B for Full Grammar specification."""
    return x + x

if __name__ == "__main__":
    assert test_ref_10_1_b(3) == 6
