r"""Test 2290 — gen #36 r244 (expected FAIL): route #244 witness. `m(self, s)` does `s.add(1)` on a set PARAMETER of a `@mutable_state` method;
the caller `c()` passes its local `s` and then reads `1 in s`. CPython returns True, so
`\result == False` is FALSE. At cdac19a6 the mutation lowered to the "sound no-op" `()` and
the claim PROVED; the callee's parameter is now a faithful local shadow and the caller, which
reads `s` after the call, is REFUSED (PYCSL-WHYML-COLLECTION-ALIAS).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass
from typing import Set


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class C:
    n: int = 0

    #@ assigns \nothing
    def m(self, s: Set[int]) -> None:
        s.add(1)

    #@ ensures \result == False
    #@ assigns \nothing
    def c(self) -> bool:
        s = set()
        s.add(2)
        self.m(s)
        return 1 in s


if __name__ == "__main__":
    assert C().c() is True
