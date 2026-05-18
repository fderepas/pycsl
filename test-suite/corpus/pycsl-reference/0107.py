"""Test 0107 — PyCSL Annotation Reference 3.2.4 (variation B)"""
_ = 0  # anchor
#@ ensures \result >= 0 and \result == x * x
def test_and_square(x: int) -> int:
    """And in ensures: non-negative and equals x squared."""
    return x * x

if __name__ == "__main__":
    assert test_and_square(3) == 9
