r"""Test 10282 -- lvZ2 restricted Path type separation (expected FAIL): a modelled `Path(<str>)`
passed to the imported `keep(x: str) -> str` through a DOTTED module callee (red team rt70 m20,
INTRODUCED by batch C); CPython: False. The modelled value is the abstract `py_path`: a Why3
TYPE ERROR (fail-closed).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
import multi_file_lib.lvz2_pathlib


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = multi_file_lib.lvz2_pathlib.keep(Path(s))
    return q == str(Path(s))


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
