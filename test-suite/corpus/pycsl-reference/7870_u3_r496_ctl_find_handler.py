r"""Test 7870 -- route #496 (control, expected PASS): g calls only never-raising methods (`s.find("z")`, `s.split(",")`, `s.strip()`, `len`); g returns `len(s) + 1`; f catches ValueError around it and returns 0 there; `ensures \result == len(s) + 1`; CPython f("a") returns 2
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

#@ ensures \result == len(s) + 1
def g(s: str) -> int:
    y = s.find("z")
    p = s.strip().split(",")
    q = len(p)
    return len(s) + 1


#@ ensures \result == len(s) + 1
def f(s: str) -> int:
    try:
        return g(s)
    except ValueError:
        return 0


if __name__ == "__main__":
    assert f("a") == 2 and f("a,b") == 4
