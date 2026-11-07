r"""Test 5438 -- gen #37 systematic rule GD / route #388 (expected FAIL): red team 30 `g05_getattr_namedtuple_count` -- `getattr(o, name, 0)` folded to the default although CPython finds the attribute; PROVED at base 7bf752d4e (CPython: VIOLATION f = <built-in method count of P object at 0x75fdb846ef00>). REFUSED (PYCSL-R376-GETATTR-CLASS-BINDING: the lookup is not fully modelled).
"""
# pycsl-expected: FAIL
from typing import NamedTuple


class P(NamedTuple):
    x: int


#@ ensures \result == 0
def f(p: P) -> int:
    return getattr(p, "count", 0)


if __name__ == "__main__":
    r = f(P(1))
    print("VIOLATION f =", r) if r != 0 else print("no violation")
