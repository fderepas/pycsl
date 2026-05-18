"""Test 0441 — Python Reference 6.2.10.4: Asynchronous generator-iterator methods (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_2_10_4_a(x: int) -> int:
    """Variation A for Asynchronous generator-iterator methods."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_2_10_4_a(4) == 5
