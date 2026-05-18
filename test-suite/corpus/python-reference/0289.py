"""Test 0289 — Python Reference 3.1: Objects, values and types (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_1_a(x: int) -> int:
    """Variation A for Objects, values and types."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_1_a(4) == 5
