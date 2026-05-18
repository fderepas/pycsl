"""Test 0491 — Python Reference 8.9.1: Coroutine function definition (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_8_9_1_a(x: int) -> int:
    """Variation A for Coroutine function definition."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_8_9_1_a(4) == 5
