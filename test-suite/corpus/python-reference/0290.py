"""Test 0290 — Python Reference 3.1: Objects, values and types (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_1_b(x: int) -> int:
    """Variation B for Objects, values and types."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_1_b(3) == 6
