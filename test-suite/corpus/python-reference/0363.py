"""Test 0363 — Python Reference 3.3.13: Special method lookup (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_13_a(x: int) -> int:
    """Variation A for Special method lookup."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_13_a(4) == 5
