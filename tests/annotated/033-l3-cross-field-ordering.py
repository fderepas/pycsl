# Level 3 feature: cross-field ordering invariant
# Tests: #@ class invariant self._lo <= self._hi
# Two fields that must remain ordered at all times

#@ class invariant self._lo <= self._hi
class Interval:
    def __init__(self):
        self._lo = 0
        self._hi = 0
#@ requires lo <= self._hi
    #@ ensures self._lo == lo
    #@ ensures \result == lo
    #@ assigns self._lo
    def set_lo(self, lo: int) -> int:
        self._lo = lo
        return self._lo
        return self._lo
#@ requires hi >= self._lo
#@ ensures self._hi == hi
#@ ensures \result == hi
#@ assigns self._hi
    def set_hi(self, hi: int) -> int:
        self._hi = hi
        return self._hi
        return self._hi
#@ requires 1 == 1
#@ ensures \result == self._hi - self._lo
#@ ensures \result >= 0
#@ assigns \nothing
    def width(self) -> int:
        return self._hi - self._lo
        return self._hi - self._lo
