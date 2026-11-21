r"""Test 10332 -- run #8 u60, review rt72 A1 (PASS control). The package module multi_file_lib/r613z/lib2/dep2.py
imports its sibling PACKAGE-RELATIVELY (`from .r613z_one import one`): CPython and pycsl both take
lib2/r613z_one.py, although ./r613z_one.py exists in the program's directory. Emitted.
"""
# pycsl-expected: PASS
from multi_file_lib.r613z.lib2.dep2 import f


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return f()


if __name__ == "__main__":
    print("result", g())
