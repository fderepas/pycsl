# Level 3 feature: monotone accumulator with invariant
# Tests: #@ class invariant self._total >= 0 on a class that only adds

class Accumulator:
    def __init__(self):
        self._total = 0

#@ requires 1 == 1
    #@ ensures self._total == \old(self._total) + n
    #@ ensures \result == \old(self._total) + n
    #@ assigns self._total
    def add(self, n: int) -> int:
        self._total += n
        return self._total

#@ requires 1 == 1
    #@ ensures \result == self._total
    #@ assigns \nothing
    def value(self) -> int:
        return self._total
