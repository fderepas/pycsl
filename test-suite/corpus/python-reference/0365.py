"""Test 0365 — Python Reference 3.4.1: Awaitable Objects (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_4_1_a(x: int) -> int:
    """Variation A for Awaitable Objects."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_4_1_a(4) == 5
