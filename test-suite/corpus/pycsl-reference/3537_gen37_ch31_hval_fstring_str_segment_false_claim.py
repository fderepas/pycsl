r"""Test 3537 — gen #37 ch31 (expected FAIL): 3536 with `\result == "0!"` (the `hint_of`
reading of a string carrier): false in CPython.
"""
# pycsl-expected: FAIL
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "0!"
#@ assigns \nothing
def g() -> str:
    d: Dict[str, PyVal] = {"n": "ab"}
    n = d.get("n")
    return f"{n}!"
