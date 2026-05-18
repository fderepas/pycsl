"""Test 0385 — Python Reference 4.3: Exceptions (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_4_3_a(x: int) -> int:
    """Variation A for Exceptions."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_4_3_a(4) == 5
