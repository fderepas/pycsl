"""PyCSL mock for Python's copyreg module — Register pickle support functions."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/copyreg.html#copyreg.constructor
#@ requires True
#@ ensures True
def constructor(object: int) -> int:
    """Mock: Declares *object* to be a valid constructor.  If *object* is not callable (and hence not valid as a constructor), raises..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/copyreg.py
#@ requires True
#@ ensures True
def pickle(type_: int, function_: int, constructor_ob: int) -> int:
    """Mock: Declares that *function* should be used as a 'reduction' function for objects of type *type*.  *function* must return ei..."""
    return 0
