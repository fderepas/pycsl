"""Test 0023 — PyCSL Annotation Reference 3.2.3"""
_ = 0  # anchor
#@ ensures \result >= 0 or \result < 0
def test_or_operator(x: int) -> int:
    """Logical or in contracts."""
    return x

if __name__ == "__main__":
    assert test_or_operator(5) == 5
    assert test_or_operator(-3) == -3
