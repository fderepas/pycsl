"""Test 0082 — PyCSL Annotation Reference 3.1.2 (variation A)"""
_ = 0  # anchor
#@ requires a >= 0
#@ requires b >= 0
#@ ensures \result == a + b
def test_two_vars(a: int, b: int) -> int:
    """Var atom: two variable references in contracts."""
    return a + b

if __name__ == "__main__":
    assert test_two_vars(3, 7) == 10
