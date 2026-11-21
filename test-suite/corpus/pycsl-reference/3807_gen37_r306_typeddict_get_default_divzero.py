r"""Test 3807 -- gen #37 route #306 (expected FAIL): TypedDict `.get("a", 10 // x)` under `no_exception \all`: the dropped default still raises in Python.
"""
# pycsl-expected: FAIL
from typing import TypedDict

class TD(TypedDict):
    a: int

#@ no_exception \all
#@ ensures \result == t["a"]
def f(t: TD, x: int) -> int:
    return t.get("a", 10 // x)

if __name__ == "__main__":
    assert f({"a": 5}, 0) == 5
