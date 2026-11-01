r"""Test 7870 -- route #496 (control, expected PASS): g calls only never-raising methods (`s.find("z")`, `s.split(",")`, `s.strip()`, `len`); f catches ValueError around it; CPython f("a") returns 1
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

#@ ensures \result == 1
def g(s: str) -> int:
    y = s.find("z")
    p = s.strip().split(",")
    q = len(p)
    return 1


#@ ensures \result == 1
def f(s: str) -> int:
    try:
        return g(s)
    except ValueError:
        return 2


if __name__ == "__main__":
    assert f("a") == 1 and f("a,b") == 1
