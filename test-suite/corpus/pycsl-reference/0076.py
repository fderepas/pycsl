"""Test 0076 — PyCSL Annotation Reference 2.3.1 (variation A)"""
""  # pycsl
#@ class invariant self._x >= 0 and self._y >= 0
class Point:
    def __init__(self):
        self._x = 0
        self._y = 0

    #@ requires dx >= 0
    #@ ensures self._x == \old(self._x) + dx
    #@ assigns self._x
    def move_x(self, dx: int) -> int:
        self._x = self._x + dx
        return self._x

if __name__ == "__main__":
    p = Point()
    assert p.move_x(3) == 3
