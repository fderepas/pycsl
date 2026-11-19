r"""Test 5642 -- gen #37 route #398 (expected FAIL): `d.a` on `d: TD` under `no_exception`; PROVED at base 3b2d2e763 (CPython: AttributeError). REFUSED (PYCSL-R398-TYPEDDICT-ACCESS).
"""
# pycsl-expected: FAIL
from typing import TypedDict


class TD(TypedDict):
    a: int


#@ no_exception \all
def f(d: TD) -> int:
    return d.a


if __name__ == "__main__":
    try:
        print("result", f({"a": 1}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
