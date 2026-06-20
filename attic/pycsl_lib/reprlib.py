"""PyCSL mock for Python's reprlib module — Alternate repr() implementation with size limits."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def repr(obj: int) -> int:
    """Mock: This is the :meth:`~Repr.repr` method of ``aRepr``.  It returns a string similar to that returned by the built-in functi..."""
    return 0
