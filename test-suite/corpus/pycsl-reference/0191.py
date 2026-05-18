"""Test 0191 — PyCSL Annotation Reference 2.3.1 (cross-field invariant)"""
""  # pycsl
#@ class invariant self._lo <= self._hi
class Interval:
    def __init__(self):
        self._lo = 0
        self._hi = 0

    #@ requires lo <= self._hi
    #@ ensures self._lo == lo
    #@ assigns self._lo
    def set_lo(self, lo: int) -> None:
        self._lo = lo

    #@ requires hi >= self._lo
    #@ ensures self._hi == hi
    #@ assigns self._hi
    def set_hi(self, hi: int) -> None:
        self._hi = hi

    #@ ensures \result == self._hi - self._lo
    #@ assigns \nothing
    def width(self) -> int:
        return self._hi - self._lo

if __name__ == "__main__":
    iv = Interval()
    iv.set_hi(10)
    iv.set_lo(3)
    assert iv.width() == 7
