r"""Test 5446 -- gen #37 systematic rule TC / route #391 (expected FAIL): red team 30 `n12_isinstance_typeddict` -- a `typing.Protocol` / `TypedDict` class used as a VALUE under `no_exception`; PROVED at base 7bf752d4e (CPython: VIOLATION TypeError TypedDict does not support instance and ). REFUSED (PYCSL-TC-TYPING-CONSTRUCT-VALUE).
"""
# pycsl-expected: FAIL
from typing import Any, TypedDict


class TD(TypedDict):
    a: int


#@ no_exception \all
def f(x: Any) -> bool:
    return isinstance(x, TD)


if __name__ == "__main__":
    try:
        f({"a": 1})
        print("no violation")
    except TypeError as e:
        print("VIOLATION TypeError", e)
