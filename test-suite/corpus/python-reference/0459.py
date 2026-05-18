"""Test 0459 — Python Reference 7.1: Expression statements (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_expr_stmt_a(x: int) -> int:
    """Expression statement followed by return."""
    y = x + 1
    return y

if __name__ == "__main__":
    assert test_expr_stmt_a(4) == 5
