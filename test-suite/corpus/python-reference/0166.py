"""Test 0166 — Python Reference 6.16: Evaluation order"""
# pycsl-expected: FAIL
# (#49) route #126: the nested `f` READS AND WRITES `order`, a local of its enclosing function.
# A lifted nested def turned that into a fresh/global name (the emitted `f` appended to its OWN
# array and the enclosing `assert order == [1, 2, 3]` was never connected to it). A lifted def
# that captures an enclosing name is REFUSED now, so this coverage test is expected-FAIL.
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
