"""Test 0361 — Python Reference 3.3.12: Annotations (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_12_a(x: int) -> int:
    """Variation A for Annotations."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_12_a(4) == 5
