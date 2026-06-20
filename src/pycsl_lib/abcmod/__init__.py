# pycsl_lib/abcmod — pure-Python abc module model
# Named 'abcmod' to avoid stdlib name clash.
#
# Contracts derived from library_reference/abc.rst.
# RST: "A decorator indicating abstract methods."
# RST: "Returns cls, to allow usage as a class decorator."
# RST: "ABCMeta — metaclass for defining ABCs."
# RST: "get_cache_token() — returns the current ABC cache token."


#@ requires func >= 0
#@ ensures \result == func
def abstractmethod(func: int) -> int:
    """RST: 'A decorator indicating abstract methods.'
    Returns the function unchanged (it is just marked)."""
    return func


#@ requires func >= 0
#@ ensures \result == func
def abstractclassmethod(func: int) -> int:
    """RST (deprecated): Mark a classmethod as abstract. Returns unchanged."""
    return func


#@ requires func >= 0
#@ ensures \result == func
def abstractstaticmethod(func: int) -> int:
    """RST (deprecated): Mark a staticmethod as abstract. Returns unchanged."""
    return func


#@ requires old_cls >= 0
#@ ensures \result == old_cls
def update_abstractmethods(old_cls: int) -> int:
    """RST: 'Recalculate an abstract class's abstraction status.
    Returns cls, to allow usage as a class decorator.'
    Returns cls unchanged."""
    return old_cls


# --- ABCMeta class ---

""  # pycsl
#@ class invariant self._registry_size >= 0
#@ class invariant self._cache_token >= 0
class ABCMeta:
    """RST: 'Metaclass for defining Abstract Base Classes (ABCs).
    Use this metaclass to create an ABC.'"""

    def __init__(self):
        self._registry_size = 0
        self._cache_token = 0

    #@ requires subclass >= 0
    #@ ensures self._registry_size == \old(self._registry_size) + 1
    #@ ensures self._cache_token == \old(self._cache_token) + 1
    #@ assigns self._registry_size, self._cache_token
    def register(self, subclass: int) -> None:
        """RST: 'Register subclass as a "virtual subclass" of this ABC.'
        Increments registry size and cache token."""
        self._registry_size = self._registry_size + 1
        self._cache_token = self._cache_token + 1

    #@ ensures \result == self._registry_size
    #@ assigns \nothing
    def registry_size(self) -> int:
        """Number of registered virtual subclasses."""
        return self._registry_size

    #@ ensures \result == self._cache_token
    #@ assigns \nothing
    def get_cache_token(self) -> int:
        """RST: 'Returns the current abstract base class cache token.
        The token changes every time a virtual subclass is registered.'"""
        return self._cache_token
