"""Test 0156 — PyCSL Annotation Reference 2.1.4 (variation A)"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result == n + n
#@ \variant n
def double_rec(n: int) -> int:
    """Recursive doubling with variant."""
    if n == 0:
        return 0
    return 2 + double_rec(n - 1)

if __name__ == "__main__":
    assert double_rec(5) == 10
