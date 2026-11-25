r"""Test 10476 -- run #9 u73, route #632 control (PASS). A wildcard of a package whose `__init__` has a
literal `__all__ = ["k"]` and no module-level `__getattr__` / `__dir__`; the submodule k is benign, nothing
names `__all__` elsewhere, so `cd <tree root> && python <this file>` prints "result 1" and pycsl proves it.
"""
# pycsl-expected: PASS
from zu73o import *
import zu73q


#@ ensures \result == 1
def g() -> int:
    return zu73q.one()


if __name__ == "__main__":
    print("result", g())
