"""Test 0505 — Python Reference 9.2: File input (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_9_2_a(x: int) -> int:
    """Variation A for File input."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_9_2_a(4) == 5
