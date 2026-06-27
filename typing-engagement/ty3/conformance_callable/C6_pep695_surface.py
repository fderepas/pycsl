# C6 PEP 695 SURFACE CONFIRMATION: the PEP 695 `type_params` field (parsed by
# `pure_ast.py`, commit 8335eede; emitted on IR v1.4 type_decls/functions;
# consumed by `monomorphize.py`, commit 89f3acec) flows end-to-end. A
# `class C[T]` declaration parses, IR-tracks `type_params`, and monomorphizes
# on `C[int]()`. This confirms the PEP 695 surface is first-class alongside
# `Callable`. (Already graduated by the TypeVar/Generic Gate C; this is the
# confirmation driver for the final TY3 construct.)


#@ class invariant self._size >= 0 and self._size <= \length(self._items)
class Cell[T]:
    def __init__(self):
        self._items = [0, 0, 0, 0]
        self._size = 0

    #@ requires self._size < \length(self._items)
    #@ ensures self._size == \old(self._size) + 1
    #@ ensures self._items[\old(self._size)] == v
    #@ assigns self._items[self._size], self._size
    def put(self, v: T) -> None:
        self._items[self._size] = v
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ ensures \result == \old(self._items[self._size - 1])
    #@ assigns self._size
    def take(self) -> T:
        self._size = self._size - 1
        return self._items[self._size]


if __name__ == "__main__":
    c = Cell[int]()
    c.put(7)
    r = c.take()
    #@ assert r == 7
