"""NO-BLEND gate (D1) — an un-instantiated generic must NOT claim a per-instance
theorem it never emitted.

Per the two-plane spec §3 D1: the static plane produces a per-instantiation
theorem (Stack_int.pop returns int, provable because the int specialization was
emitted). The runtime plane produces a generic-alias object (Stack[int] is a
GenericAlias, NO specialized proof). Letting the runtime alias stand in for the
static theorem is the coherent-and-wrong failure.

This driver asserts the no-blend invariant: a generic that is NEVER
instantiated with `int` must NOT have an int per-instance postcondition. The
only specialization emitted is `Stack_bool`; an `assert r == 7` (the int
theorem) would have NO specialization to carry it → no VC discharges.
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
    # ONLY a bool specialization is collected — no Stack_int is emitted.
    s = Stack[bool]()
    s.push(1)
    r = s.pop()
    #@ assert r == 1
