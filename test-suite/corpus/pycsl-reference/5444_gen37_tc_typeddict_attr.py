r"""Test 5444 -- gen #37 systematic rule TC / route #391 (expected FAIL): red team 30 `m02_typeddict_attr` -- a `typing.Protocol` / `TypedDict` class used as a VALUE under `no_exception`; PROVED at base 7bf752d4e (CPython: VIOLATION AttributeError 'dict' object has no attribute 'a'). REFUSED (PYCSL-TC-TYPING-CONSTRUCT-VALUE).
"""
# pycsl-expected: FAIL
from typing import TypedDict


class TD(TypedDict):
    a: int


#@ no_exception \all
def f() -> int:
    t = TD(a=1)
    return t.a  # type: ignore


if __name__ == "__main__":
    try:
        f()
        print("no violation")
    except AttributeError as e:
        print("VIOLATION AttributeError", e)
