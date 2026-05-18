"""Test 0163 — Python Reference 6.13: Conditional expressions"""
_ = 0  # anchor
#@ ensures \result == 5
def test_conditional_expressions() -> int:
    """x if cond else y."""
    x = 5
    return x if x > 0 else -x

if __name__ == "__main__":
    assert test_conditional_expressions() == 5
