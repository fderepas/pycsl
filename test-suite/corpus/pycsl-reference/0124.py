"""Test 0124 — PyCSL Annotation Reference 3.4.4 (variation A)"""
""  # pycsl
#@ class invariant self._val >= 0
class Box:
    def __init__(self):
        self._val = 0

    #@ requires v >= 0
    #@ ensures self._val == v
    #@ assigns self._val
    def set_val(self, v: int) -> None:
        self._val = v

if __name__ == "__main__":
    b = Box()
    b.set_val(10)
    assert b._val == 10
