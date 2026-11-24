r"""Test 10344 -- run #8 u61, review rt74 V2D control (PASS). The package module
multi_file_lib/r613y/lib4/dep4.py imports `from .zpq61.b import one`; every prefix of the dotted name is a
regular package inside lib4/, so the prefix-consistency rule and the per-prefix comparison both hold and
CPython loads the file pycsl verified: `cd <tree root> && python <this file>` prints "result 1".
"""
# pycsl-expected: PASS
from multi_file_lib.r613y.lib4.dep4 import f


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return f()


if __name__ == "__main__":
    print("result", g())
