r"""Test 7874 -- route #496 (control, expected PASS): g holds `s.index("z")` but the caller makes no claim a dead handler could falsify (`ensures True`) and has no handler; f2 has a handler and calls only a never-raising helper; CPython f2("a") returns 1
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional

#@ ensures True
def g(s: str) -> int:
    y = s.index("a")
    return 1


#@ ensures \result >= 0
def h(s: str) -> int:
    return len(s)


#@ ensures \result == 1
def f2(s: str) -> int:
    try:
        h(s)
    except ValueError:
        return 2
    return 1


if __name__ == "__main__":
    assert g("a") == 1 and f2("a") == 1
