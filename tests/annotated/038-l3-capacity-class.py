# Level 3 feature: capacity constraint invariant
# Tests: #@ class invariant self._size <= self._capacity
# A fixed-capacity buffer; push is guarded by capacity

#@ class invariant self._size >= 0
#@ class invariant self._capacity > 0
#@ class invariant self._size <= self._capacity
class Buffer:
    def __init__(self):
        self._size = 0
        self._capacity = 10
#@ requires 1 == 1
    #@ ensures \result == self._size
    #@ ensures \result >= 0
    #@ ensures \result <= self._capacity
    #@ ensures \old(self._size) < self._capacity ==> self._size == \old(self._size) + 1
    #@ ensures \old(self._size) == self._capacity ==> self._size == \old(self._size)
    #@ assigns self._size
    def push(self, n: int) -> int:
        if self._size < self._capacity:
            self._size += 1
        return self._size
        return self._size
#@ requires 1 == 1
#@ ensures self._size == 0
#@ ensures \result == 0
#@ assigns self._size
    def clear(self) -> int:
        self._size = 0
        return self._size
        return self._size
#@ requires 1 == 1
    #@ ensures \result == self._capacity - self._size
    #@ ensures \result >= 0
    #@ assigns \nothing
    def free(self) -> int:
        return self._capacity - self._size
        return self._capacity - self._size
