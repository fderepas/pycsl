"""Test 0029 — PyCSL Annotation Reference 3.2.9"""
_ = 0  # anchor
#@ ensures \result >= 0
def test_unary_operators(x: int) -> int:
    """Unary operators: not, -, + in contracts."""
    if x >= 0:
        return +x
    return -x

if __name__ == "__main__":
    assert test_unary_operators(-5) == 5
    assert test_unary_operators(3) == 3
