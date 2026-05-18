"""Test 0368 — Python Reference 3.4.3: Asynchronous Iterators (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_4_3_b(x: int) -> int:
    """Variation B for Asynchronous Iterators."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_4_3_b(3) == 6
