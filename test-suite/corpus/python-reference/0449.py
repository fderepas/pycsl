"""Test 0449 — Python Reference 6.4: Await expression (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_4_a(x: int) -> int:
    """Variation A for Await expression."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_4_a(4) == 5
