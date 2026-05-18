"""Test 0427 — Python Reference 6.2.1: Built-in constants (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_6_2_1_a(x: int) -> int:
    """Variation A for Built-in constants."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_6_2_1_a(4) == 5
