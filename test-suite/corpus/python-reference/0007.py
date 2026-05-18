"""Test 0007 — Python Reference 2.1.5: Explicit line joining"""
_ = 0  # anchor
#@ ensures \result == a + b + c
def test_explicit_line_joining(a: int, b: int, c: int) -> int:
    """Backslash continues a logical line."""
    result = a + \
             b + \
             c
    return result

if __name__ == "__main__":
    assert test_explicit_line_joining(1, 2, 3) == 6
