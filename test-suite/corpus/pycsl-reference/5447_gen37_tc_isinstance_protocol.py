r"""Test 5447 -- gen #37 systematic rule TC / route #391 (expected FAIL): red team 30 `n13_isinstance_protocol` -- a `typing.Protocol` / `TypedDict` class used as a VALUE under `no_exception`; PROVED at base 7bf752d4e (CPython: VIOLATION TypeError Instance and class checks can only be us). REFUSED (PYCSL-TC-TYPING-CONSTRUCT-VALUE).
"""
# pycsl-expected: FAIL
from typing import Any, Protocol


class P(Protocol):
    def m(self) -> int:
        ...


#@ no_exception \all
def f(x: Any) -> bool:
    return isinstance(x, P)


if __name__ == "__main__":
    try:
        f(1)
        print("no violation")
    except TypeError as e:
        print("VIOLATION TypeError", e)
