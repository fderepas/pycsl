"""Test 0009 — Python Reference 2.1.7: Blank lines"""
_ = 0  # anchor
#@ ensures \result == x
def test_blank_lines(x: int) -> int:
    """Blank lines separate logical sections."""

    y = x

    return y

if __name__ == "__main__":
    assert test_blank_lines(7) == 7
