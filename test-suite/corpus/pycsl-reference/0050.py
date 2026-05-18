"""Test 0050 — PyCSL Annotation Reference 2.1.5: Structural variant"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result >= 0
#@ \variant (n, subterm)
def count_down(n: int) -> int:
    """Structural variant test (expected UNPROVEN — needs Why3 theory)."""
    if n <= 0:
        return 0
    return count_down(n - 1) + 1

if __name__ == "__main__":
    assert count_down(0) == 0
    assert count_down(5) == 5
    print("PASS")
