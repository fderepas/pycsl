"""Test 0211 — Python Reference 8.10.2: Generic classes"""
# (#44) WAS `pycsl-expected: FAIL`, and it PROVES today. Its contract is TRUE of the
# program, so this is a CAPABILITY GAIN, not a soundness regression — the construct
# it exercises became supported after the file was written. Found by making the
# suite report XPASS as a FAILURE: until then an expected-FAIL test that started
# proving was reported PASS, which made all 241 negative witnesses unenforceable.
# pycsl-expected: PASS
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
