"""Test 0010 — PyCSL Annotation Reference 3.1.3"""
# pycsl-expected: FAIL
""  # pycsl
#@ class invariant self._val >= 0
class Holder:
    def __init__(self):
        self._val = 0

    #@ ensures self._val == v
    #@ assigns self._val
    def set_val(self, v: int) -> None:
        self._val = v

if __name__ == "__main__":
    h = Holder()
    h.set_val(5)
    assert h._val == 5
