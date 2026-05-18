"""Test 0031 — PyCSL Annotation Reference 3.4.2"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_assigns_variable(x: int) -> int:
    """Assigns variable: a single variable may be mutated."""
    y = x + 1
    return y

if __name__ == "__main__":
    assert test_assigns_variable(9) == 10
