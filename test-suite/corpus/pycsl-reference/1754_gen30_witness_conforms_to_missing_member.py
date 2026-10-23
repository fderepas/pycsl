r"""Test 1754 — WITNESS: `#@ conforms_to` on a class that does not provide a protocol
member.

"Conformance requires every protocol member to be present with a refining contract" — a
class declaring conformance while missing `m` would inherit the protocol's guarantees at
call sites without ever providing them. Sibling of 1753.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from typing import Protocol

_ = 0  # anchor


class P(Protocol):
    #@ ensures \result >= 0
    def m(self) -> int:
        ...


#@ conforms_to P
class C:
    #@ ensures \result == 0
    def other(self) -> int:
        return 0
