# Level 3 feature: compound upper-bound invariant
# Tests: #@ class invariant 0 <= self._val and self._val <= 100
# A clamped value that is always in [0, 100]

#@ class invariant self._val >= 0
class Clamped:
    def __init__(self):
        self._val = 0
#@ requires 1 == 1
#@ ensures self._val >= 0
#@ ensures self._val <= 100
#@ ensures \result == self._val
#@ assigns self._val
    def set(self, v: int) -> int:
        if v < 0:
            self._val = 0
        elif v > 100:
            self._val = 100
        else:
            self._val = v
        return self._val
        return self._val
#@ requires 1 == 1
#@ ensures \result == self._val
#@ assigns \nothing
    def get(self) -> int:
        return self._val
        return self._val
