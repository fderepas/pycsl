"""Test 0092 — Python Reference 3.3.8: Emulating numeric types"""
_ = 0  # anchor
#@ ensures \result == 6
def test_emulating_numeric_types() -> int:
    """__add__, __sub__, __mul__, etc."""
    class N:
        def __init__(self, v):
            self._v = v
        def __add__(self, other):
            return N(self._v + other._v)
        def __mul__(self, other):
            return N(self._v * other._v)
        def value(self):
            return self._v
    a = N(2)
    b = N(3)
    return (a * b).value()

if __name__ == "__main__":
    assert test_emulating_numeric_types() == 6
