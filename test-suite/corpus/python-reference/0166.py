"""Test 0166 — Python Reference 6.16: Evaluation order"""
_ = 0  # anchor
#@ ensures \result == 0
def test_evaluation_order() -> int:
    """Python evaluates left to right."""
    order = []
    def f(x):
        order.append(x)
        return x
    _ = f(1) + f(2) + f(3)
    assert order == [1, 2, 3]
    return 0

if __name__ == "__main__":
    assert test_evaluation_order() == 0
