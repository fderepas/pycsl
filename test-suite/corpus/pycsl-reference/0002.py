"""Test 0002 — PyCSL Annotation Reference 2.1.2"""
_ = 0  # anchor
#@ ensures \result == x * x
def test_postcondition(x: int) -> int:
    """Postcondition: ensures must hold at function exit."""
    return x * x

if __name__ == "__main__":
    assert test_postcondition(3) == 9
    assert test_postcondition(-2) == 4
