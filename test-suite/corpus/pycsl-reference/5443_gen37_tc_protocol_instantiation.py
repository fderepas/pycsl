r"""Test 5443 -- gen #37 systematic rule TC / route #391 (expected FAIL): red team 30 `j08_protocol_instantiation` -- a `typing.Protocol` / `TypedDict` class used as a VALUE under `no_exception`; PROVED at base 7bf752d4e (CPython: VIOLATION TypeError Protocols cannot be instantiated). REFUSED (PYCSL-TC-TYPING-CONSTRUCT-VALUE).
"""
# pycsl-expected: FAIL
from typing import Protocol


class P(Protocol):
    def m(self) -> int:
        ...


class Q(P, Protocol):
    pass


#@ no_exception \all
def f() -> None:
    Q()


if __name__ == "__main__":
    try:
        f()
        print("no violation")
    except TypeError as e:
        print("VIOLATION TypeError", e)
