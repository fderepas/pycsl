"""Test 0161 — Python Reference 6.11: Boolean operations"""
_ = 0  # anchor
#@ ensures \result == 1
def test_boolean_operations() -> int:
    """and, or, not."""
    if True and not False:
        return 1
    return 0

if __name__ == "__main__":
    assert test_boolean_operations() == 1
