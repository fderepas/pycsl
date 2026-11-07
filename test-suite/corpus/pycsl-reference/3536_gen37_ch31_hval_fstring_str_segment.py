r"""Test 3536 — gen #37 ch31 (expected PASS): an f-string segment holding an `HStr s` hval renders as
`s` (CPython: "ab!"). At 0f7cb454 it was `int_to_string (hint_of _)`, a fresh arbitrary string: the
claim could not prove.
"""
from typing import Any, Dict

PyVal = Any


#@ ensures \result == "ab!"
#@ assigns \nothing
def g() -> str:
    d: Dict[str, PyVal] = {"n": "ab"}
    n = d.get("n")
    return f"{n}!"
