"""Test 0225 — PyCSL Annotation Reference 3.2.8 (modulo in contract)"""
_ = 0  # anchor
#@ requires n > 0
#@ ensures \result == n % 2
def test_parity(n: int) -> int:
    return n % 2

if __name__ == "__main__":
    assert test_parity(10) == 0
    assert test_parity(7) == 1
