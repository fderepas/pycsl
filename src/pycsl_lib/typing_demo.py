"""Formal driver for the typing stub (the my_os_demo.py analog).

Exercises the stub's identity / constant / passthrough contracts end-to-end. Verifies with
**zero** `\trusted`: each wrapper's postcondition is discharged from the callee's `ensures`."""
from typing import List, Optional, cast, TypeVar, overload


#@ requires x >= 0
#@ ensures \result == x
def demo_alias(x: int) -> int:
    """A type alias (List) is the identity on its argument."""
    return List(x)


#@ ensures \result == x
def demo_optional(x: int) -> int:
    """Optional[...] is the identity special form."""
    return Optional(x)


#@ ensures \result == v
def demo_cast(tp: int, v: int) -> int:
    """cast(T, v) returns v unchanged."""
    return cast(tp, v)


#@ ensures \result >= 0
def demo_typevar(name: str) -> int:
    """TypeVar(name) is an opaque non-negative handle."""
    return TypeVar(name)


#@ ensures \result == f
def demo_overload(f: int) -> int:
    """The overload decorator is a passthrough."""
    return overload(f)
