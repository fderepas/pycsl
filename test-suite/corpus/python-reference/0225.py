"""Test 0225 — Python Reference 2.1.2: Physical lines (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_1_2_a(x: int) -> int:
    """Variation A for Physical lines."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_1_2_a(4) == 5
