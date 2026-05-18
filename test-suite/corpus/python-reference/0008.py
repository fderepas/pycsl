"""Test 0008 — Python Reference 2.1.6: Implicit line joining"""
_ = 0  # anchor
#@ ensures \result == a + b + c
def test_implicit_line_joining(a: int, b: int, c: int) -> int:
    """Expressions in brackets can span multiple physical lines."""
    result = (a +
              b +
              c)
    return result

if __name__ == "__main__":
    assert test_implicit_line_joining(1, 2, 3) == 6
