"""Test 0509 — Python Reference 10.1: Full Grammar specification (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_10_1_a(x: int) -> int:
    """Variation A for Full Grammar specification."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_10_1_a(4) == 5
