"""Test 0114 — PyCSL Annotation Reference 3.2.8 (variation A)"""
_ = 0  # anchor
#@ ensures \result == a * b
def test_mul(a: int, b: int) -> int:
    """Multiplication operator."""
    return a * b

if __name__ == "__main__":
    assert test_mul(3, 7) == 21
