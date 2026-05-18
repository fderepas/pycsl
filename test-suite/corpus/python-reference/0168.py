"""Test 0168 — Python Reference 7.1: Expression statements"""
_ = 0  # anchor
#@ ensures \result == 0
def test_expression_statements() -> int:
    """An expression used as a statement."""
    x = 42  # expression statement
    return 0

if __name__ == "__main__":
    assert test_expression_statements() == 0
