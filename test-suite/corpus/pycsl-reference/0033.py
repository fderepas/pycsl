"""Test 0033 — PyCSL Annotation Reference 3.4.4"""
""  # pycsl
#@ class invariant self._x >= 0
class PosHolder:
    def __init__(self):
        self._x = 0

    #@ requires v >= 0
    #@ ensures self._x == v
    #@ assigns self._x
    def set_x(self, v: int) -> None:
        self._x = v

if __name__ == "__main__":
    h = PosHolder()
    h.set_x(5)
    assert h._x == 5
