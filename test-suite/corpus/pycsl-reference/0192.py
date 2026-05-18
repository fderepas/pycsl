"""Test 0192 — PyCSL Annotation Reference 2.3.1 (multiple stacked invariants)"""
""  # pycsl
#@ class invariant self._size >= 0
#@ class invariant self._capacity > 0
#@ class invariant self._size <= self._capacity
class Buffer:
    def __init__(self):
        self._size = 0
        self._capacity = 10

    #@ requires self._size < self._capacity
    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def push(self) -> None:
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ assigns self._size
    def pop(self) -> None:
        self._size = self._size - 1

    #@ ensures \result == self._size
    #@ assigns \nothing
    def count(self) -> int:
        return self._size

if __name__ == "__main__":
    b = Buffer()
    b.push()
    b.push()
    assert b.count() == 2
    b.pop()
    assert b.count() == 1
