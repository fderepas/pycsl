"""PyCSL mock for Python's dataclasses module — Generate special methods on user-defined classes."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def field(default: int, default_factory: int, init: int, repr: int, hash: int, compare: int, metadata: int) -> int:
    """Mock: For common and simple use cases, no other functionality is required.  There are, however, some dataclass features that r..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fields(class_or_instance: int) -> int:
    """Mock: Returns a tuple of :class:`Field` objects that define the fields for this dataclass.  Accepts either a dataclass, or an ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def asdict(obj: int, dict_factory: int) -> int:
    """Mock: Converts the dataclass *obj* to a dict (by using the factory function *dict_factory*).  Each dataclass is converted to a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def astuple(obj: int, tuple_factory: int) -> int:
    """Mock: Converts the dataclass *obj* to a tuple (by using the factory function *tuple_factory*).  Each dataclass is converted to..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def make_dataclass(cls_name: int, fields: int, bases: int, namespace: int, init: int, repr: int, eq: int) -> int:
    """Mock: Creates a new dataclass with name *cls_name*, fields as defined in *fields*, base classes as given in *bases*, and initi..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def replace(obj: int) -> int:
    """Mock: Creates a new object of the same type as *obj*, replacing fields with values from *changes*.  If *obj* is not a Data Cla..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_dataclass(obj: int) -> int:
    """Mock: Return ``True`` if its parameter is a dataclass (including subclasses of a dataclass, but not including :ref:`generic al..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def __post_init__() -> int:
    """Mock: When defined on the class, it will be called by the generated :meth:`~object.__init__`, normally as :meth:`!self.__post_..."""
    return 0
