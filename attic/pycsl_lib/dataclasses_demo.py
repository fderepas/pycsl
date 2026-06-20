"""Formal driver for the dataclasses stub (the my_os_demo.py analog).

The dataclasses utilities are decorator / introspection sentinels (there is no real computation
to model on ints — `@dataclass` is a passthrough, `field`/`fields`/`asdict` return descriptors).
This driver exercises their contracts end-to-end; verifies with **zero** `\trusted`."""
from dataclasses import dataclass, is_dataclass, fields


#@ ensures \result == c
def demo_dataclass(c: int) -> int:
    """The @dataclass decorator returns the class unchanged."""
    return dataclass(c)


#@ ensures \result == 0 or \result == 1
def demo_is_dataclass(obj: int) -> int:
    """is_dataclass returns a 0/1 flag."""
    return is_dataclass(obj)


#@ ensures \result >= 0
def demo_fields(c: int) -> int:
    """fields returns a non-negative descriptor handle."""
    return fields(c)
