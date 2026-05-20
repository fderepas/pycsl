"""Test 0217 — Python Reference 9.4: Expression input"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 5
def test_expression_input() -> int:
    """eval() evaluates a single expression."""
    return eval("2 + 3")

if __name__ == "__main__":
    assert test_expression_input() == 5
