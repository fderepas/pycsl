"""Test 0392 — Python Reference 5.2.1: Regular packages (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_2_1_b(x: int) -> int:
    """Variation B for Regular packages."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_2_1_b(3) == 6
