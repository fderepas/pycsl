"""Test 0388 — Python Reference 4.4.2: Python Runtime Model (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_4_4_2_b(x: int) -> int:
    """Variation B for Python Runtime Model."""
    return x + x

if __name__ == "__main__":
    assert test_ref_4_4_2_b(3) == 6
