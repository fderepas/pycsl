r"""Test 5643 -- gen #37 route #398 (expected FAIL): functional TypedDict with a `NotRequired` key; `d["b"]` under `no_exception`; PROVED at base 3b2d2e763 (CPython: KeyError). REFUSED (PYCSL-R398-TYPEDDICT-ACCESS).
"""
# pycsl-expected: FAIL
from typing import NotRequired, TypedDict

TD = TypedDict("TD", {"a": int, "b": NotRequired[int]})


#@ no_exception \all
def f(d: TD) -> int:
    return d["b"]


if __name__ == "__main__":
    try:
        print("result", f({"a": 1}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
