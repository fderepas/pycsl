"""Test 0422 — Python Reference 5.7: Package Relative Imports (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_7_b(x: int) -> int:
    """Variation B for Package Relative Imports."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_7_b(3) == 6
