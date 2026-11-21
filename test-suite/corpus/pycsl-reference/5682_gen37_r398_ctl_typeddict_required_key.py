r"""Test 5682 -- gen #37 CONTROL route #398 (expected PASS): a REQUIRED key `d["a"]` of a TypedDict with a `NotRequired` sibling, in a contract and a body under `no_exception`; PROVED (CPython 2).
"""
# pycsl-expected: PASS
from typing import NotRequired, TypedDict
class TD(TypedDict):
    a: int
    b: NotRequired[int]
#@ no_exception \all
#@ ensures \result == d["a"] + 1
def f(d: TD) -> int:
    return d["a"] + 1
if __name__ == "__main__":
    print("result", f({"a": 1}))
