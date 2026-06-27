"""TY3 monomorphization — two instantiations (Stack[int] + Stack[str]).

The pass should emit TWO specialized copies: `Stack_int` and `Stack_str`, each
with its substituted contract. This is the no-blend guard (D1): the int
specialization carries the int postcondition; the str specialization carries the
str postcondition — NEITHER plane's claim stands in for the other.
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
    si = Stack[int]()
    si.push(7)
    ri = si.pop()
    ss = Stack[str]()
    ss.push("hi")
    rs = ss.pop()
    #@ assert ri == 7
    #@ assert rs == "hi"
