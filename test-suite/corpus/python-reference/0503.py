"""Test 0503 — Python Reference 9.1: Complete Python programs (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_9_1_a(x: int) -> int:
    """Variation A for Complete Python programs."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_9_1_a(4) == 5
