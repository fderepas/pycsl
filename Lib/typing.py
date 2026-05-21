"""PyCSL mock for Python's typing module — Support for type hints (see :pep:`484`)."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def cast(typ: int, val_: int) -> int:
    """Mock: Cast a value to a type. This returns the value unchanged.  To the type checker this signals that the return value has th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def assert_type(val_: int, typ: int) -> int:
    """Mock: Ask a static type checker to confirm that *val* has an inferred type of *typ*. At runtime this does nothing: it returns ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def assert_never(arg: int) -> int:
    """Mock: Ask a static type checker to confirm that a line of code is unreachable. Example:: def int_or_str(arg: int | str) -> Non..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def reveal_type(obj: int) -> int:
    """Mock: Ask a static type checker to reveal the inferred type of an expression. When a static type checker encounters a call to ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_overloads(func: int) -> int:
    """Mock: Return a sequence of :deco:`overload`-decorated definitions for *func*. *func* is the function object for the implementa..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def clear_overloads() -> int:
    """Mock: Clear all registered overloads in the internal registry. This can be used to reclaim the memory used by the registry. ....."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_type_hints(obj: int, globalns: int, localns: int, include_extras: int, format: int) -> int:
    """Mock: Return a dictionary containing type hints for a function, method, module, class object, or other callable object. This i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_origin(tp: int) -> int:
    """Mock: Get the unsubscripted version of a type: for a typing object of the form ``X[Y, Z, ...]`` return ``X``. If ``X`` is a ty..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_args(tp: int) -> int:
    """Mock: Get type arguments with all substitutions performed: for a typing object of the form ``X[Y, Z, ...]`` return ``(Y, Z, ....."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_protocol_members(tp: int) -> int:
    """Mock: Return the set of members defined in a :class:`Protocol`. .. doctest:: >>> from typing import Protocol, get_protocol_mem..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_protocol(tp: int) -> int:
    """Mock: Determine if a type is a :class:`Protocol`. For example: .. testcode:: class P(Protocol): def a(self) -> str: ... b: int..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_typeddict(tp: int) -> int:
    """Mock: Check if a type is a :class:`TypedDict`. For example: .. testcode:: class Film(TypedDict): title: str year: int assert i..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def evaluate_forward_ref(forward_ref: int, owner: int, globals: int, locals: int, type_params: int, format: int) -> int:
    """Mock: Evaluate an :class:`annotationlib.ForwardRef` as a :term:`type hint`. This is similar to calling :meth:`annotationlib.Fo..."""
    return 0
