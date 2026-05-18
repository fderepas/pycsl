"""Test 0393 — Python Reference 5.2.2: Namespace packages (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_2_2_a(x: int) -> int:
    """Variation A for Namespace packages."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_2_2_a(4) == 5
