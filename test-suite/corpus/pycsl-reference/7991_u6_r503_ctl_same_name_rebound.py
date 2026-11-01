r"""Test 7991 -- route #503 (control, expected PASS): `a is a` on a rebound name -- one name read twice is one object; CPython True
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


#@ ensures \result == True
def f(n: int) -> bool:
    a = n + 1
    a = a * 1000
    return a is a


if __name__ == "__main__":
    assert f(5) == True
