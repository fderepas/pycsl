"""Test 0506 — Python Reference 9.2: File input (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_9_2_b(x: int) -> int:
    """Variation B for File input."""
    return x + x

if __name__ == "__main__":
    assert test_ref_9_2_b(3) == 6
