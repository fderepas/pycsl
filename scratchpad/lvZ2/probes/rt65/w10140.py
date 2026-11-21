r"""Test 10140 -- lvX `Path(<str>)` model (expected PASS): `Path(s)` is the deterministic, law-free
`val function ext_path_of_str_op` of the string (pathlib parsing is lexical), so two paths built
from the SAME `str` are equal (CPython: always).
"""
# pycsl-expected: PASS
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    return Path(s) == Path(s)


if __name__ == "__main__":
    r = same("a//b/")
    print("VIOLATION contract" if r is not True else "result", r)
