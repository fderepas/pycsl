r"""Test 10249 -- route #617 (expected FAIL): a `Path(<str>)` passed to the IMPORTED
`keep(x: str) -> str` (red team rt67 m05, INTRODUCED by batch C); `q == str(Path(s))` PROVED
`\result == True`, CPython False (`keep` returns the Path itself). REFUSED
(`PYCSL-R614-PATH-STR-CONFLATED`: a Path argument to an imported parameter not annotated Path).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from multi_file_lib.r617_pathlib import keep


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = keep(Path(s))
    return q == str(Path(s))


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
