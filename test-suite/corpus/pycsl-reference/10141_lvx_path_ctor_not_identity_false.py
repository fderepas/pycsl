r"""Test 10141 -- lvX `Path(<str>)` model (expected FAIL): the model is LAW-FREE, not the identity:
CPython normalises `Path("a//b")` to `a/b`, so `str(Path(s)) == s` is False for `s = "a//b"` and
`\result == True` must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def ident(s: str) -> bool:
    return str(Path(s)) == s


if __name__ == "__main__":
    r = ident("a//b")
    print("VIOLATION contract" if r is not True else "result", r)
