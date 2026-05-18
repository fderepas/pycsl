"""Test 0401 — Python Reference 5.3.4: The meta path (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_3_4_a(x: int) -> int:
    """Variation A for The meta path."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_3_4_a(4) == 5
