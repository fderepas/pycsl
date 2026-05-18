"""Test 0165 — Python Reference 6.15: Expression lists"""
_ = 0  # anchor
#@ ensures \result == 6
def test_expression_lists() -> int:
    """Comma-separated expressions form tuples."""
    a, b, c = 1, 2, 3
    return a + b + c

if __name__ == "__main__":
    assert test_expression_lists() == 6
