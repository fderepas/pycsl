"""Test 0492 — Python Reference 8.9.1: Coroutine function definition (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_8_9_1_b(x: int) -> int:
    """Variation B for Coroutine function definition."""
    return x + x

if __name__ == "__main__":
    assert test_ref_8_9_1_b(3) == 6
