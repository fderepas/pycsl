"""Test 0450 — Python Reference 6.4: Await expression (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_4_b(x: int) -> int:
    """Variation B for Await expression."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_4_b(3) == 6
