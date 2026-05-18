"""Test 0439 — Python Reference 6.2.10.3: Asynchronous generator functions (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_2_10_3_a(x: int) -> int:
    """Variation A for Asynchronous generator functions."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_2_10_3_a(4) == 5
