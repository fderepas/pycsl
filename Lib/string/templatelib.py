"""PyCSL mock for Python's string.templatelib module — Support for template string literals."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def convert(obj: int, conversion: int) -> int:
    """Mock: Applies formatted string literal :ref:`conversion <formatstrings-conversion>` semantics to the given object *obj*. This ..."""
    return 0
