"""Test 0387 — Python Reference 4.4.2: Python Runtime Model (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_4_4_2_a(x: int) -> int:
    """Variation A for Python Runtime Model."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_4_4_2_a(4) == 5
