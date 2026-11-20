r"""Test 10246 -- route #617 (expected FAIL): a Path alias IMPORTED from another module
(`multi_file_lib/r617_pathlib.py`: `Fp: TypeAlias = Path`); `p == str(p)` on an `Fp` parameter;
CPython False. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`: the dependency's aliases are read from its
source).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from multi_file_lib.r617_pathlib import Fp


#@ ensures \result == True
#@ assigns \nothing
def f(p: Fp) -> bool:
    return p == str(p)


if __name__ == "__main__":
    from pathlib import Path
    r = f(Path("a"))
    print("VIOLATION contract" if r is not True else "result", r)
