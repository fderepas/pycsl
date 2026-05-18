"""Test 0067 — PyCSL Annotation Reference 2.1.1 (variation B)"""
_ = 0  # anchor
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result >= 0
def test_precondition_two_args(a: int, b: int) -> int:
    """Precondition with two parameters."""
    return a + b

if __name__ == "__main__":
    assert test_precondition_two_args(3, 4) == 7
