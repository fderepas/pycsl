"""Test 0102 — PyCSL Annotation Reference 3.2.2 (variation A)"""
_ = 0  # anchor
#@ ensures x >= 0 ==> \result == x
#@ ensures x < 0 ==> \result == 0 - x
def test_abs_impl(x: int) -> int:
    """Implication: absolute value via implies."""
    if x >= 0:
        return x
    return 0 - x

if __name__ == "__main__":
    assert test_abs_impl(5) == 5
    assert test_abs_impl(-3) == 3
