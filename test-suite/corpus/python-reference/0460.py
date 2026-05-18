"""Test 0460 — Python Reference 7.1: Expression statements (variation B)"""
_ = 0  # anchor
#@ ensures \result == a * a
def test_expr_stmt_b(a: int) -> int:
    """Expression statement with multiplication."""
    result = a * a
    return result

if __name__ == "__main__":
    assert test_expr_stmt_b(5) == 25
