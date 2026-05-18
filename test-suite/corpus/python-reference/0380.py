"""Test 0380 — Python Reference 4.2.4: Lazy evaluation (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_4_2_4_b(x: int) -> int:
    """Variation B for Lazy evaluation."""
    return x + x

if __name__ == "__main__":
    assert test_ref_4_2_4_b(3) == 6
