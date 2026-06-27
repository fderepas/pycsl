"""S5 STATIC gate — G2/G3: two concrete instantiations yield two name-mangled
specialized copies, each with its substituted contract provable.

Per the two-plane spec §1.7: `Stack[int]` yields `Stack_int` whose `pop` returns
`int`; a `Stack[str]` specialization returns `str` and is a SEPARATE proof. The
int postcondition on `pop` is provable on the int specialization; the str
postcondition is NOT stateable on the int copy (the no-blend invariant, D1).

This driver is the int specialization (the str one is S5_str.py). The gate
asserts the per-instantiation int postcondition discharges.
"""
_ = 0  # anchor
#@ class invariant self._size >= 0 and self._size <= \length(self._items)
class Stack[T]:
    def __init__(self):
        self._items = [0, 0, 0, 0, 0, 0, 0, 0]
        self._size = 0

    #@ requires self._size < \length(self._items)
    #@ ensures self._size == \old(self._size) + 1
    #@ ensures self._items[\old(self._size)] == v
    #@ assigns self._items[self._size], self._size
    def push(self, v: T) -> None:
        self._items[self._size] = v
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ ensures \result == \old(self._items[self._size - 1])
    #@ assigns self._size
    def pop(self) -> T:
        self._size = self._size - 1
        return self._items[self._size]

if __name__ == "__main__":
    s = Stack[int]()
    s.push(7)
    r = s.pop()
    #@ assert r == 7
