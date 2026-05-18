"""Test 0087 — PyCSL Annotation Reference 3.1.5 (variation B)"""
_ = 0  # anchor
#@ ensures \result >= 0
#@ ensures \result == x * x
def test_result_non_negative(x: int) -> int:
    """Result in multiple ensures clauses."""
    return x * x

if __name__ == "__main__":
    assert test_result_non_negative(-3) == 9
