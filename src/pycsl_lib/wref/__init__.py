# pycsl_lib/wref — pure-Python weakref module model
# Named 'wref' to avoid stdlib name clash.
#
# Contracts derived from library_reference/weakref.rst.
# RST: "The weakref module allows the Python programmer to create
#  weak references to objects."
# RST: "ref(), proxy(), getweakrefcount(), getweakrefs()"
#
# Model: weak references as integer ids with alive/dead state.


#@ requires obj >= 0
#@ ensures \result == obj
#@ assigns \nothing
def ref(obj: int) -> int:
    """RST: 'Return a weak reference to object.'
    Model: ref is the object id itself (alive state implicit)."""
    return obj


#@ requires obj >= 0
#@ ensures \result == obj
#@ assigns \nothing
def proxy(obj: int) -> int:
    """RST: 'Return a proxy to object which uses a weak reference.'
    Proxy behaves like the object."""
    return obj


#@ requires obj >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def getweakrefcount(obj: int) -> int:
    """RST: 'Return the number of weak references to object.'
    Non-negative count."""
    return 0


#@ requires obj >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def getweakrefs_count(obj: int) -> int:
    """RST: 'Return a list of all weak reference objects that refer to object.'
    Returns count of weak references."""
    return 0


""  # pycsl
#@ class invariant self._size >= 0
class WeakValueDictionary:
    """RST: 'Mapping class that references values weakly.'"""

    def __init__(self):
        self._size = 0

    #@ requires key >= 0
    #@ requires val >= 0
    #@ ensures self._size == \old(self._size) + 1
    #@ assigns self._size
    def set(self, key: int, val: int) -> None:
        """Add a key-value pair (weak reference to value)."""
        self._size = self._size + 1

    #@ ensures \result == self._size
    #@ assigns \nothing
    def size(self) -> int:
        """Number of live entries."""
        return self._size

    #@ requires self._size > 0
    #@ ensures self._size == \old(self._size) - 1
    #@ assigns self._size
    def discard(self, key: int) -> None:
        """Remove an entry."""
        self._size = self._size - 1
