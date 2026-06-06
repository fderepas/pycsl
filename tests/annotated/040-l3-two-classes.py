# Level 3 feature: two classes, each with its own class invariant
# Tests that multiple type_decls each carry independent invariants

class Up:
    def __init__(self):
        self._x = 0

#@ requires 1 == 1
    #@ ensures self._x == \old(self._x) + n
    #@ ensures \result == self._x
    #@ assigns self._x
    def inc(self, n: int) -> int:
        self._x += n
        return self._x

#@ requires 1 == 1
    #@ ensures \result == self._x
    #@ assigns \nothing
    def get(self) -> int:
        return self._x


#@ class invariant self._y >= 0
class Down:
    def __init__(self):
        self._y = 100
#@ requires n >= 0
    #@ requires n <= self._y
    #@ ensures self._y == \old(self._y) - n
    #@ ensures \result == self._y
    #@ assigns self._y
    def dec(self, n: int) -> int:
        self._y -= n
        return self._y
        return self._y
#@ requires 1 == 1
    #@ ensures \result == self._y
    #@ assigns \nothing
    def get(self) -> int:
        return self._y
        return self._y
