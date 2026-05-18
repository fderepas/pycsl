"""Test 0004 — Python Reference 2.1.2: Physical lines"""
_ = 0  # anchor
#@ ensures \result == x
def test_physical_lines(x: int) -> int:
    """A physical line ends with a newline."""
    y = x
    return y

if __name__ == "__main__":
    assert test_physical_lines(42) == 42
