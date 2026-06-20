# Formal tests for pycsl_lib/copyreg
from pycsl_lib.copyreg import pickle, constructor


#@ requires obj_type >= 0
#@ requires func >= 0
#@ ensures \result >= 0
def test_pickle_nonneg(obj_type: int, func: int) -> int:
    """pickle returns non-negative registration id."""
    return pickle(obj_type, func)


#@ requires func >= 0
#@ ensures \result == func
def test_constructor_identity(func: int) -> int:
    """constructor returns func unchanged."""
    return constructor(func)
