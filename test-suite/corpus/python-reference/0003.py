"""Test 0003 — Python Reference 2.1.1: Logical lines"""
_ = 0  # anchor
#@ ensures \result == a + b
def test_logical_lines(a: int, b: int) -> int:
    """A logical line is composed of one or more physical lines."""
    result = (a +
              b)
    return result

if __name__ == "__main__":
    assert test_logical_lines(10, 20) == 30
