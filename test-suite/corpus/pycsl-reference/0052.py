"""Test 0052 — PyCSL Annotation Reference 2.1.7: Trusted (correct body)"""
_ = 0  # anchor
#@ ensures \result == 2 * x
#@ \trusted
def double_int(x: int) -> int:
    """Trusted function — body not verified, contract assumed."""
    return x + x

#@ ensures \result == 2 * x
def foobar(x: int) -> int:
    """Calls trusted double_int — postcondition proven from assumed contract."""
    return double_int(x)

if __name__ == "__main__":
    assert double_int(3) == 6
    assert foobar(5) == 10
    print("PASS")
