"""Test 0379 — Python Reference 4.2.4: Lazy evaluation (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_4_2_4_a(x: int) -> int:
    """Variation A for Lazy evaluation."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_4_2_4_a(4) == 5
