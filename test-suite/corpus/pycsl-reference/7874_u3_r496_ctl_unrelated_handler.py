r"""Test 7874 -- route #496 (control, expected PASS): f's handler surrounds a call of a never-raising program helper h (`len(s)`); `ensures \result == len(s)` holds because the handler is really dead; CPython f("ab") returns 2
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


#@ ensures \result == len(s)
def h(s: str) -> int:
    return len(s)


#@ ensures \result == len(s)
def f(s: str) -> int:
    r = 0
    try:
        r = h(s)
    except ValueError:
        r = -1
    return r


if __name__ == "__main__":
    assert f("ab") == 2 and f("") == 0
