"""Test 0504 — Python Reference 9.1: Complete Python programs (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_9_1_b(x: int) -> int:
    """Variation B for Complete Python programs."""
    return x + x

if __name__ == "__main__":
    assert test_ref_9_1_b(3) == 6
