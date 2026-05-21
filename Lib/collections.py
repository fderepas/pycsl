"""PyCSL mock for Python's collections module — Container datatypes."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def namedtuple(typename: int, field_names: int, rename: int, defaults: int, module_: int) -> int:
    """Mock: Returns a new tuple subclass named *typename*.  The new subclass is used to create tuple-like objects that have fields a..."""
    return 0
