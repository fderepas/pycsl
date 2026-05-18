"""Test 0335 — Python Reference 3.3.2.2: Implementing Descriptors (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_2_2_a(x: int) -> int:
    """Variation A for Implementing Descriptors."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_2_2_a(4) == 5
