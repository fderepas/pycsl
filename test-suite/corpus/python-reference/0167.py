"""Test 0167 — Python Reference 6.17: Operator precedence"""
_ = 0  # anchor
#@ ensures \result == 0
def test_operator_precedence() -> int:
    """Operator precedence: * before +, etc."""
    assert 2 + 3 * 4 == 14
    assert (2 + 3) * 4 == 20
    return 0

if __name__ == "__main__":
    assert test_operator_precedence() == 0
