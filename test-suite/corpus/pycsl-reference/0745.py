"""Test 0745 — PyCSL Annotation Reference 7.5 (lambda lexical capture)"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result >= n
def test_capture(n: int) -> int:
    add_n = lambda a: a + n   # captures the outer parameter n
    return add_n(0)

if __name__ == "__main__":
    assert test_capture(7) == 7
    assert test_capture(0) == 0
