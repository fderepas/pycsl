"""Test 0049 — PyCSL Annotation Reference 2.1.4: Function variant (integer)"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result >= 1
#@ \variant n
def factorial(n: int) -> int:
    """Recursive factorial with integer variant."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

if __name__ == "__main__":
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(5) == 120
    print("PASS")
