r"""Test 10202 -- route #614 (expected FAIL): Path ORDERING decided as string ordering (rt65 g01).
CPython orders Paths by parts: `Path("a/b") < Path("a-b")` is True while `"a/b" < "a-b"` is False,
so `(p < q) == (str(p) < str(q))` is False for ("a/b", "a-b"); PROVED `\result == True` at
4d753c2f1. REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path


#@ ensures \result == True
#@ assigns \nothing
def f(s: str, t: str) -> bool:
    p = Path(s)
    q = Path(t)
    return (p < q) == (str(p) < str(q))


if __name__ == "__main__":
    r = f("a/b", "a-b")
    print("VIOLATION contract" if r is not True else "result", r)
