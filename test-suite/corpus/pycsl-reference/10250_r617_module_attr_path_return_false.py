r"""Test 10250 -- route #617 (expected FAIL): the module-attribute spelling of 10247
(`import multi_file_lib.r617_pathlib as lib`; `p = lib.mk(s)`); CPython `p == str(p)` False.
REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
import multi_file_lib.r617_pathlib as lib


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = lib.mk(s)
    return p == str(p)


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
