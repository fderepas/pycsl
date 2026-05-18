"""Test 0115 — PyCSL Annotation Reference 3.2.8 (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * x * x
def test_cube(x: int) -> int:
    """Multiplication: cube."""
    return x * x * x

if __name__ == "__main__":
    assert test_cube(3) == 27
