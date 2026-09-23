r"""Test 1839 — ROUTE #223 CONTROL (expected PASS): a DECLARATION-ONLY protocol is untouched.

Route #223's refusal must be about a member that carries an IMPLEMENTATION, not about
`Protocol` as such. This file declares the member the way PEP 544 and this compiler's own
comment describe — an `...` body — and the conforming class implements it and is CHECKED
against the protocol's contract. It must keep verifying.

Without this control the repair would be indistinguishable from a ban on the feature, which
is exactly the over-broad shape route #13's census refused once already.
"""
# pycsl-expected: PASS
from typing import Protocol
_ = 0  # anchor


class P(Protocol):
    #@ ensures \result == 99
    def m(self) -> int: ...


class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 99
    def m(self) -> int:
        return 99


#@ ensures \result == 99
def use() -> int:
    c = C()
    return c.m()
