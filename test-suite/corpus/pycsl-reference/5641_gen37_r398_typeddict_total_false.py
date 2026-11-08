r"""Test 5641 -- gen #37 route #398 (expected FAIL): `class TD(TypedDict, total=False)`; `d["a"]` under `no_exception`; PROVED at base 3b2d2e763 (CPython: KeyError). REFUSED (PYCSL-R398-TYPEDDICT-ACCESS).
"""
# pycsl-expected: FAIL
from typing import TypedDict


class TD(TypedDict, total=False):
    a: int


#@ no_exception \all
def f(d: TD) -> int:
    return d["a"]


if __name__ == "__main__":
    try:
        print("result", f({}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
