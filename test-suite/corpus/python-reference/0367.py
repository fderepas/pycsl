"""Test 0367 — Python Reference 3.4.3: Asynchronous Iterators (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_4_3_a(x: int) -> int:
    """Variation A for Asynchronous Iterators."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_4_3_a(4) == 5
