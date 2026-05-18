"""Test 0442 — Python Reference 6.2.10.4: Asynchronous generator-iterator methods (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_2_10_4_b(x: int) -> int:
    """Variation B for Asynchronous generator-iterator methods."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_2_10_4_b(3) == 6
