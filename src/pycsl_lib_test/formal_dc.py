# Formal tests for pycsl_lib/dc — dataclasses module
from pycsl_lib.dc import fields, dataclass, is_dataclass


#@ requires cls >= 0
#@ ensures \result >= 0
def test_fields_nonneg(cls: int) -> int:
    """fields returns non-negative count."""
    return fields(cls)


#@ requires cls >= 0
#@ ensures \result >= 0
def test_dataclass_nonneg(cls: int) -> int:
    """dataclass decorator returns non-negative."""
    return dataclass(cls)


#@ requires obj >= 0
#@ ensures \result >= 0
def test_is_dataclass_nonneg(obj: int) -> int:
    """is_dataclass returns non-negative."""
    return is_dataclass(obj)
