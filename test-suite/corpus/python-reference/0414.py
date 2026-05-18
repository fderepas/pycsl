"""Test 0414 — Python Reference 5.4.6: Cached bytecode invalidation (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_4_6_b(x: int) -> int:
    """Variation B for Cached bytecode invalidation."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_4_6_b(3) == 6
