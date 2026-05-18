"""Test 0012 — PyCSL Annotation Reference 3.1.5"""
_ = 0  # anchor
#@ ensures \result == x * x
def test_result(x: int) -> int:
    """Result atom: \result refers to the return value in ensures."""
    return x * x

if __name__ == "__main__":
    assert test_result(4) == 16
