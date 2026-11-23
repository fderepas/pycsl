r"""Test 10381 -- run #9 u66, route #621 control (PASS). The package zr81's __init__ binds its submodule `b`
by `from . import b` (exactly that submodule) and an alias `b1` that names no submodule, so the attribute
zr81.b is the submodule pycsl verifies: `cd <tree root> && python <this file>` prints "result 1".
"""
# pycsl-expected: PASS
import zr81.b


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return zr81.b.one()


if __name__ == "__main__":
    print("result", g())
