"""Test 0440 — Python Reference 6.2.10.3: Asynchronous generator functions (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_2_10_3_b(x: int) -> int:
    """Variation B for Asynchronous generator functions."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_2_10_3_b(3) == 6
