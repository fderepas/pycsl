"""Test 0366 — Python Reference 3.4.1: Awaitable Objects (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_4_1_b(x: int) -> int:
    """Variation B for Awaitable Objects."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_4_1_b(3) == 6
