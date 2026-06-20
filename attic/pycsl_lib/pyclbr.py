"""PyCSL mock for Python's pyclbr module — Supports information extraction for a Python module browser."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def readmodule(module_: int, path: int) -> int:
    """Mock: Return a dictionary mapping module-level class names to class descriptors.  If possible, descriptors for imported base c..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def readmodule_ex(module_: int, path: int) -> int:
    """Mock: Return a dictionary-based tree containing a function or class descriptors for each function and class defined in the mod..."""
    return 0
