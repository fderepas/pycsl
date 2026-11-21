r"""Test 10254 -- route #617 (expected FAIL): the WILDCARD-import spelling of 10247
(`from multi_file_lib.r617_pathlib import *`; `p = mk(s)`; lvZ probe q10, PRE-EXISTING: emitted
as `str_eq_op !p !p`); CPython `p == str(p)` False. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from multi_file_lib.r617_pathlib import *


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = mk(s)
    return p == str(p)


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
