"""Test 0391 — Python Reference 5.2.1: Regular packages (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_2_1_a(x: int) -> int:
    """Variation A for Regular packages."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_2_1_a(4) == 5
