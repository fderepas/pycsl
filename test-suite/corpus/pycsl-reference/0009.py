"""Test 0009 — PyCSL Annotation Reference 3.1.2"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result == x + 1
def test_variable_reference(x: int) -> int:
    """Var atom: variable reference in contracts."""
    return x + 1

if __name__ == "__main__":
    assert test_variable_reference(9) == 10
