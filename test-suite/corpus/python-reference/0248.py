"""Test 0248 — Python Reference 2.3.3: Reserved classes of identifiers (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_3_3_b(x: int) -> int:
    """Variation B for Reserved classes of identifiers."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_3_3_b(3) == 6
