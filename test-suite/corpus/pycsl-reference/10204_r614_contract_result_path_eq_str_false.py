r"""Test 10204 -- route #614 (expected FAIL): the conflation in a CONTRACT. `-> Path` returns its
`p: Path` parameter and claims `\result == str(p)`: CPython `p == str(p)` is False, so the
postcondition is false for every call; the model equates a Path with its string. REFUSED on the
contract (`PYCSL-R614-PATH-STR-CONFLATED`, the IR clause site).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == str(p)
#@ assigns \nothing
def f(p: Path) -> Path:
    return p


if __name__ == "__main__":
    r = f(Path("a"))
    print("VIOLATION contract" if r != str(Path("a")) else "result", r)
