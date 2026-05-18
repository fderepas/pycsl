"""Test 0036 — PyCSL Annotation Reference 4.2"""
_ = 0  # anchor
#@ ensures \result >= 0
def test_no_modulo(x: int) -> int:
    """% (modulo) is NOT supported in contracts."""
    if x >= 0:
        return x
    return -x

if __name__ == "__main__":
    assert test_no_modulo(-7) == 7
