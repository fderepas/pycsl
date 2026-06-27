"""TY3 feasibility probe — Step 2/3: hand-monomorphized Stack_int (T -> int).

What the future monomorphization machinery would emit for `Stack[int]`:
ONE name-mangled specialized WhyML let/val with the TypeVar T substituted by int.
We hand-write it to prove the path discharges end-to-end BEFORE the
collection/emission machinery exists. The driver's contract depends on the int
instantiation (`ensures \result == v`).
"""
_ = 0  # anchor
#@ class invariant self._size >= 0 and self._size <= \length(self._items)
class Stack_int:
    def __init__(self):
        self._items = [0, 0, 0, 0, 0, 0, 0, 0]
        self._size = 0

    #@ requires self._size < \length(self._items)
    #@ ensures self._size == \old(self._size) + 1
    #@ ensures self._items[\old(self._size)] == v
    #@ assigns self._items[self._size], self._size
    def push(self, v: int) -> None:
        self._items[self._size] = v
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ ensures \result == \old(self._items[self._size - 1])
    #@ assigns self._size
    def pop(self) -> int:
        self._size = self._size - 1
        return self._items[self._size]

if __name__ == "__main__":
    s = Stack_int()
    s.push(7)
    r = s.pop()
    #@ assert r == 7
