"""Test 0419 — Python Reference 5.6: Replacing the standard import system (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_6_a(x: int) -> int:
    """Variation A for Replacing the standard import system."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_6_a(4) == 5
