"""Test 0075 — Python Reference 3.3.1: Basic customization"""
_ = 0  # anchor
#@ ensures \result == 0
def test_basic_customization() -> int:
    """__init__, __del__, __repr__, __str__, __hash__, __bool__."""
    class C:
        def __init__(self, v):
            self._v = v
        def __repr__(self):
            return f"C({self._v})"
        def __bool__(self):
            return self._v != 0
    c = C(0)
    assert not c
    return 0

if __name__ == "__main__":
    assert test_basic_customization() == 0
