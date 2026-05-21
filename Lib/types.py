"""PyCSL mock for Python's types module — Names for built-in types."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def new_class(name: int, bases: int, kwds: int, exec_body: int) -> int:
    """Mock: Creates a class object dynamically using the appropriate metaclass. The first three arguments are the components that ma..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def prepare_class(name: int, bases: int, kwds: int) -> int:
    """Mock: Calculates the appropriate metaclass and creates the class namespace. The arguments are the components that make up a cl..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def resolve_bases(bases: int) -> int:
    """Mock: Resolve MRO entries dynamically as specified by :pep:`560`. This function looks for items in *bases* that are not instan..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_original_bases(cls: int) -> int:
    """Mock: Return the tuple of objects originally given as the bases of *cls* before the :meth:`~object.__mro_entries__` method has..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def DynamicClassAttribute(fget: int, fset: int, fdel: int, doc: int) -> int:
    """Mock: Route attribute access on a class to __getattr__. This is a descriptor, used to define attributes that act differently w..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def coroutine(gen_func: int) -> int:
    """Mock: This function transforms a :term:`generator` function into a :term:`coroutine function` which returns a generator-based ..."""
    return 0
