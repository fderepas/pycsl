"""Test 0086 — PyCSL Annotation Reference 3.1.5 (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + y
def test_result_sum(x: int, y: int) -> int:
    """Result atom with addition."""
    return x + y

if __name__ == "__main__":
    assert test_result_sum(3, 4) == 7
