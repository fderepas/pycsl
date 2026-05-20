"""Test 0211 — Python Reference 8.10.2: Generic classes"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 0
def test_generic_classes() -> int:
    """Generic classes with type parameters."""
    class Box[T]:
        def __init__(self, val: T):
            self.val = val
    b = Box(42)
    assert b.val == 42
    return 0

if __name__ == "__main__":
    assert test_generic_classes() == 0
