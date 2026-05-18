"""Test 0041 — Python Reference 3.2.3: Ellipsis"""
_ = 0  # anchor
#@ ensures \result == 0
def test_ellipsis_type() -> int:
    """Ellipsis (...) is the sole value of types.EllipsisType."""
    x = ...
    if x is Ellipsis:
        return 0
    return 1

if __name__ == "__main__":
    assert test_ellipsis_type() == 0
