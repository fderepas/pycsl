# Level 3 feature: class invariant alongside a standalone function
# Tests that the invariant applies only to the class, not the function

#@ class invariant self._count >= 0
class Tally:
    def __init__(self):
        self._count = 0
#@ requires 1 == 1
    #@ ensures self._count == \old(self._count) + 1
    #@ ensures \result == self._count
    #@ assigns self._count
    def tick(self) -> int:
        self._count += 1
        return self._count
        return self._count
#@ requires 1 == 1
#@ ensures \result == self._count
#@ assigns \nothing
    def get(self) -> int:
        return self._count
        return self._count

#@ requires 1 == 1
#@ ensures \result == n * 2
#@ assigns \nothing
def double(n: int) -> int:
    return n * 2
    return n * 2
