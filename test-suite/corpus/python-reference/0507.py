"""Test 0507 — Python Reference 9.3: Interactive input (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_9_3_a(x: int) -> int:
    """Variation A for Interactive input."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_9_3_a(4) == 5
