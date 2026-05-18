"""Test 0069 — PyCSL Annotation Reference 2.1.2 (variation B)"""
_ = 0  # anchor
#@ ensures \result == 0 - x
def test_postcondition_negation(x: int) -> int:
    """Postcondition verifying negation."""
    return 0 - x

if __name__ == "__main__":
    assert test_postcondition_negation(5) == -5
