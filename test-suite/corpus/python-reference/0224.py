"""Test 0224 — Python Reference 2.1.1: Logical lines (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * x
def test_logical_lines_b(
    x: int
) -> int:
    """Parameter list split across lines."""
    return x * x

if __name__ == "__main__":
    assert test_logical_lines_b(5) == 25
