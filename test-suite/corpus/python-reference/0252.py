"""Test 0252 — Python Reference 2.5.1: Triple-quoted strings (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_2_5_1_b(x: int) -> int:
    """Variation B for Triple-quoted strings."""
    return x + x

if __name__ == "__main__":
    assert test_ref_2_5_1_b(3) == 6
