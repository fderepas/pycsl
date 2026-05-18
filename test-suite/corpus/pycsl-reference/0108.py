"""Test 0108 — PyCSL Annotation Reference 3.2.5 (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + x
def test_eq_double(x: int) -> int:
    """Equality: double via addition."""
    return x + x

if __name__ == "__main__":
    assert test_eq_double(7) == 14
