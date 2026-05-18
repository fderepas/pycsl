"""Test 0297 — Python Reference 3.2.8.4: Coroutine functions (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_2_8_4_a(x: int) -> int:
    """Variation A for Coroutine functions."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_2_8_4_a(4) == 5
