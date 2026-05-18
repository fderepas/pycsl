"""Test 0229 — PyCSL Annotation Reference 3.1.19 (None in contract)"""
_ = 0  # anchor
#@ requires x >= 0
#@ ensures \result != None
def test_none_literal(x: int) -> int:
    return x + 1

if __name__ == "__main__":
    assert test_none_literal(0) == 1
    assert test_none_literal(9) == 10
