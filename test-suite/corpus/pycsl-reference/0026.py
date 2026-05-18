"""Test 0026 — PyCSL Annotation Reference 3.2.6"""
_ = 0  # anchor
#@ requires a < b
#@ ensures \result > 0
def test_comparison_operators(a: int, b: int) -> int:
    """Comparison operators <, >, <=, >= in contracts."""
    return b - a

if __name__ == "__main__":
    assert test_comparison_operators(1, 5) == 4
