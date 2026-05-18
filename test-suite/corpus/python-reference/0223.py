"""Test 0223 — Python Reference 2.1.1: Logical lines (variation A)"""
_ = 0  # anchor
#@ ensures \result == a + b + c
def test_logical_lines_a(a: int, b: int,
                          c: int) -> int:
    """Logical line spanning three physical lines via parentheses."""
    result = (a +
              b +
              c)
    return result

if __name__ == "__main__":
    assert test_logical_lines_a(1, 2, 3) == 6
