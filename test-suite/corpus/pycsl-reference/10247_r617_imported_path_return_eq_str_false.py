r"""Test 10247 -- route #617 (expected FAIL): a Path returned by an IMPORTED function declared
`-> Path` (red team rt67 m01, PRE-EXISTING: the injected stub's return was erased to `string`, so
`p = mk(s); p == str(p)` was `str_eq_op !p !p` and PROVED); CPython False. REFUSED
(`PYCSL-R614-PATH-STR-CONFLATED`: the imported callee's declared return is read from its source).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from multi_file_lib.r617_pathlib import mk


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    p = mk(s)
    return p == str(p)


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
