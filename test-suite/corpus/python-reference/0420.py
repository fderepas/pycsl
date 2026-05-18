"""Test 0420 — Python Reference 5.6: Replacing the standard import system (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_6_b(x: int) -> int:
    """Variation B for Replacing the standard import system."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_6_b(3) == 6
