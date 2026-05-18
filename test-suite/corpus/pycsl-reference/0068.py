"""Test 0068 — PyCSL Annotation Reference 2.1.2 (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + y + 1
def test_postcondition_sum(x: int, y: int) -> int:
    """Postcondition with two parameters and addition."""
    return x + y + 1

if __name__ == "__main__":
    assert test_postcondition_sum(2, 3) == 6
