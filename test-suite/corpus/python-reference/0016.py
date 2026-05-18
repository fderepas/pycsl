"""Test 0016 — Python Reference 2.3.3: Reserved classes of identifiers"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_reserved_identifiers(x: int) -> int:
    """Names like _x, __x, __x__ have special meaning by convention."""
    _private = x
    return _private + 1

if __name__ == "__main__":
    assert test_reserved_identifiers(9) == 10
