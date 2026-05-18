"""Test 0421 — Python Reference 5.7: Package Relative Imports (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_7_a(x: int) -> int:
    """Variation A for Package Relative Imports."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_7_a(4) == 5
