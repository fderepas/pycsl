"""Test 0328 — Python Reference 3.2.13.3: Traceback objects (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_13_3_b(x: int) -> int:
    """Variation B for Traceback objects."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_13_3_b(3) == 6
