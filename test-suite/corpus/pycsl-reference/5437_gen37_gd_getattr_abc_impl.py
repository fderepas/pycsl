r"""Test 5437 -- gen #37 systematic rule GD / route #388 (expected FAIL): red team 30 `g02_getattr_abc_impl` -- `getattr(o, name, 0)` folded to the default although CPython finds the attribute; PROVED at base 7bf752d4e (CPython: VIOLATION f = <_abc._abc_data object at 0x7641672b3680>). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING: the lookup is not fully modelled).
"""
# pycsl-expected: FAIL
from abc import ABC


class R(ABC):
    def __init__(self) -> None:
        self.x: int = 1


#@ ensures \result == 0
def f(r: R) -> int:
    return getattr(r, "_abc_impl", 0)


if __name__ == "__main__":
    r = f(R())
    print("VIOLATION f =", r) if r != 0 else print("no violation")
