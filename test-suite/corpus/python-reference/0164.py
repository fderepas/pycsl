"""Test 0164 — Python Reference 6.14: Lambdas"""
_ = 0  # anchor
#@ ensures \result == 5
def test_lambdas() -> int:
    """lambda creates anonymous functions."""
    f = lambda x: x + 1
    return f(4)

if __name__ == "__main__":
    assert test_lambdas() == 5
