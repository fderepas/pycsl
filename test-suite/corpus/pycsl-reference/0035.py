"""Test 0035 — PyCSL Annotation Reference 4.1"""
_ = 0  # anchor
#@ ensures \result == x + x
def test_no_floor_division(x: int) -> int:
    """// (floor division) is NOT supported in contracts — use Python code only."""
    return x + x

if __name__ == "__main__":
    assert test_no_floor_division(5) == 10
