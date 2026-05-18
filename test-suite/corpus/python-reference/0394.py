"""Test 0394 — Python Reference 5.2.2: Namespace packages (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_2_2_b(x: int) -> int:
    """Variation B for Namespace packages."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_2_2_b(3) == 6
