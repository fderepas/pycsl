"""Test 0428 — Python Reference 6.2.1: Built-in constants (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_6_2_1_b(x: int) -> int:
    """Variation B for Built-in constants."""
    return x + x

if __name__ == "__main__":
    assert test_ref_6_2_1_b(3) == 6
