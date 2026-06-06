# Level 3 feature: invariant preserved across many mutating methods
# Tests that Why3 checks the invariant at every method boundary

#@ class invariant self._points >= 0
class Score:
    def __init__(self):
        self._points = 0
#@ requires n >= 0 - self._points * 0
    #@ requires self._points + n >= 0
    #@ ensures self._points == \old(self._points) + n
    #@ ensures \result == self._points
    #@ assigns self._points
    def add(self, n: int) -> int:
        self._points += n
        return self._points
        return self._points
#@ requires n >= 0
#@ ensures \old(self._points) >= n ==> \result == \old(self._points) - n
#@ ensures \old(self._points) < n ==> \result == \old(self._points)
#@ ensures \result >= 0
#@ ensures \result == self._points
#@ assigns self._points
    def subtract(self, n: int) -> int:
        if self._points >= n:
            self._points -= n
        return self._points
        return self._points
#@ requires 1 == 1
#@ ensures self._points == 0
#@ ensures \result == 0
#@ assigns self._points
    def reset(self) -> int:
        self._points = 0
        return self._points
        return self._points
#@ requires 1 == 1
#@ ensures \result == self._points
#@ assigns \nothing
    def get(self) -> int:
        return self._points
        return self._points
