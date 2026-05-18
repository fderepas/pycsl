"""Test 0240 — PyCSL Annotation Reference 7.4 (match statement)"""
# pycsl-flags: --no-proof
_ = 0  # anchor
#@ requires x >= 0 and x <= 2
#@ ensures \result >= 0
def test_match_basic(x: int) -> int:
    match x:
        case 0:
            return 10
        case 1:
            return 20
        case _:
            return 30

if __name__ == "__main__":
    assert test_match_basic(0) == 10
    assert test_match_basic(1) == 20
    assert test_match_basic(2) == 30
