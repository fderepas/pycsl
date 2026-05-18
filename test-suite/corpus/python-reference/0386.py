"""Test 0386 — Python Reference 4.3: Exceptions (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_4_3_b(x: int) -> int:
    """Variation B for Exceptions."""
    return x + x

if __name__ == "__main__":
    assert test_ref_4_3_b(3) == 6
