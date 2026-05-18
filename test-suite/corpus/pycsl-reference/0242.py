"""Test 0242 — PyCSL Annotation Reference 7.5 (lambda expression)"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result >= 0
def test_lambda(x: int) -> int:
    f = lambda a: a + 1
    return f(x)

if __name__ == "__main__":
    assert test_lambda(5) == 6
    assert test_lambda(0) == 1
