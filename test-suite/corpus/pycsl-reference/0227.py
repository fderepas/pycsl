"""Test 0227 — PyCSL Annotation Reference 3.1.18 (True/False in contract)"""
_ = 0  # anchor
#@ requires True
#@ ensures \result >= 0
def test_true_pre(x: int) -> int:
    if x >= 0:
        return x
    return 0 - x

if __name__ == "__main__":
    assert test_true_pre(5) == 5
    assert test_true_pre(-3) == 3
