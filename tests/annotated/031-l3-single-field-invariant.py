# Level 3 feature: single-field class invariant
# Tests: #@ class invariant 1 == 1

#@ class invariant self._n >= 0
class Counter:
    def __init__(self):
        self._n = 0
#@ requires amount >= 0
    #@ ensures self._n == \old(self._n) + amount
    #@ ensures \result == self._n
    #@ assigns self._n
    def increment(self, amount: int) -> int:
        self._n += amount
        return self._n
        return self._n
#@ requires 1 == 1
    #@ ensures self._n == 0
    #@ ensures \result == 0
    #@ assigns self._n
    def reset(self) -> int:
        self._n = 0
        return self._n
        return self._n
