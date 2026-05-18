"""Test 0247 — Python Reference 2.3.3: Reserved classes of identifiers (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_2_3_3_a(x: int) -> int:
    """Variation A for Reserved classes of identifiers."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_2_3_3_a(4) == 5
