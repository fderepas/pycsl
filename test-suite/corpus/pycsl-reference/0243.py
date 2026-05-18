"""Test 0243 — PyCSL Annotation Reference 7.5 (lambda multi-param)"""
_ = 0  # anchor
#@ requires a >= 0 and b >= 0
#@ ensures \result >= 0
def test_lambda_multi(a: int, b: int) -> int:
    add = lambda x, y: x + y
    return add(a, b)

if __name__ == "__main__":
    assert test_lambda_multi(3, 4) == 7
    assert test_lambda_multi(0, 0) == 0
