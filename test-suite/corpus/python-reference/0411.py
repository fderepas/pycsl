"""Test 0411 — Python Reference 5.4.5: Module reprs (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_4_5_a(x: int) -> int:
    """Variation A for Module reprs."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_4_5_a(4) == 5
