r"""Test 5640 -- gen #37 route #398 (expected FAIL): `d["b"]` with `b: NotRequired[int]` under `no_exception`; PROVED at base 3b2d2e763 (CPython: KeyError). REFUSED (PYCSL-R398-TYPEDDICT-ACCESS).
"""
# pycsl-expected: FAIL
from typing import NotRequired, TypedDict


class TD(TypedDict):
    a: int
    b: NotRequired[int]


#@ no_exception \all
def f(d: TD) -> int:
    return d["b"]


if __name__ == "__main__":
    try:
        print("result", {"a": 1} and f({"a": 1}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
