"""Test 0053 — PyCSL Annotation Reference 2.1.7: Trusted (wrong body)"""
_ = 0  # anchor
#@ ensures \result == 2 * x
#@ \trusted
def double_int(x: int) -> int:
    """WRONG body — returns 3*x, but trusted so not checked."""
    return x + x + x

#@ ensures \result == 2 * x
def foobar(x: int) -> int:
    """Caller still proven because trusted contract is assumed."""
    return double_int(x)

if __name__ == "__main__":
    # Dynamic check would fail: double_int(3) == 9, not 6
    # But static verification passes because body is trusted.
    print("PASS")
