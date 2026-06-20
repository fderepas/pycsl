# Pure model for array — typed array
# Models array as size-tracked container with typecode.

""" # pycsl"""


#@ class invariant self._size >= 0
#@ class invariant self._typecode >= 0
class Array:
    """Abstract typed array tracking size and type."""

    #@ requires typecode >= 0
    #@ ensures self._size == 0
    #@ ensures self._typecode == typecode
    def __init__(self, typecode: int) -> None:
        self._size: int = 0
        self._typecode: int = typecode

    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def append(self, value: int) -> None:
        """Append item to array."""
        self._size = self._size + 1

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ assigns self._size
    def pop(self) -> int:
        """Remove and return last item."""
        self._size = self._size - 1
        return 0

    #@ requires self._size > 0
    #@ requires index >= 0
    #@ requires index < self._size
    #@ ensures self._size == \old(self._size) - 1
    #@ assigns self._size
    def remove_at(self, index: int) -> None:
        """Remove item at index."""
        self._size = self._size - 1

    #@ ensures \result == self._size
    def length(self) -> int:
        """Return number of items."""
        return self._size

    #@ ensures \result == self._typecode
    def typecode(self) -> int:
        """Return typecode."""
        return self._typecode

    #@ ensures self._size == \old(self._size) + \old(self._size)
    #@ assigns self._size
    def extend_self(self) -> None:
        """Extend array with copy of itself (double size)."""
        self._size = self._size + self._size
