"""Test 0407 — Python Reference 5.4.3: Module specs (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_4_3_a(x: int) -> int:
    """Variation A for Module specs."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_4_3_a(4) == 5
