"""Test 0425 — Python Reference 5.9: References (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_9_a(x: int) -> int:
    """Variation A for References."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_9_a(4) == 5
