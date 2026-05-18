"""Test 0157 — PyCSL Annotation Reference 2.1.4 (variation B)"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result == 0
#@ \variant n
def to_zero(n: int) -> int:
    """Recursive countdown to zero."""
    if n == 0:
        return 0
    return to_zero(n - 1)

if __name__ == "__main__":
    assert to_zero(10) == 0
