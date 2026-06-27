"""TY3 monomorphization driver — Stack[int] specialization via the pass.

The generic `class Stack[T]` with two instantiation sites `Stack[int]()`.
The monomorphization pass should:
  - COLLECT the int instantiation,
  - EMIT a name-mangled specialized `Stack_int` with T -> int substituted in
    field types, signatures, and contracts,
  - REWRITE the `Stack[int]()` calls to `Stack_int()`,
  - REMOVE the original generic decl + methods (replaced by the copy).
The driver's `assert r == 7` is the per-instantiation int theorem (D1 — the
static per-instantiation postcondition the runtime generic-alias object does
NOT carry; the no-blend trap).
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
