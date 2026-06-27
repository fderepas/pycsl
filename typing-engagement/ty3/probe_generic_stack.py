"""TY3 feasibility probe — Step 1: does the PEP 695 generic front-end accept `class Stack[T]`?"""
""  # pycsl
#@ class invariant len(self._items) >= 0
class Stack[T]:
    def __init__(self):
        self._items = []

    #@ ensures len(self._items) == \old(len(self._items)) + 1
    #@ assigns self._items
    def push(self, v: T) -> None:
        self._items = self._items + [v]

    #@ requires len(self._items) > 0
    #@ ensures len(self._items) == \old(len(self._items)) - 1
    #@ ensures \result == \old(self._items[len(self._items) - 1])
    #@ assigns self._items
    def pop(self) -> T:
        last = self._items[len(self._items) - 1]
        self._items = self._items[:len(self._items) - 1]
        return last

if __name__ == "__main__":
    s: Stack[int] = Stack[int]()
    s.push(7)
    assert s.pop() == 7
