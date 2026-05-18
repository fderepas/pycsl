"""Test 0298 — Python Reference 3.2.8.4: Coroutine functions (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_2_8_4_b(x: int) -> int:
    """Variation B for Coroutine functions."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_2_8_4_b(3) == 6
