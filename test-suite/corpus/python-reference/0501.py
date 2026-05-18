"""Test 0501 — Python Reference 8.11: Annotations (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_8_11_a(x: int) -> int:
    """Variation A for Annotations."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_8_11_a(4) == 5
