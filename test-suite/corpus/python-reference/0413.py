"""Test 0413 — Python Reference 5.4.6: Cached bytecode invalidation (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_4_6_a(x: int) -> int:
    """Variation A for Cached bytecode invalidation."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_4_6_a(4) == 5
