r"""Test 1856 — ROUTE #224 CONTROL (expected PASS): a REFINING conformance still verifies.

Byte-identical to 1855 except that `C.m` promises what `P.m` promises. It verifies with NO
`# pycsl-flags`, which is the half of route #224's repair that is easy to break: the
obvious over-broad version — "emit every `overrides` refinement goal by default" — would
also turn on the IMPLICIT inheritance Liskov obligation for every based class in the
corpus, a change nobody asked for and nobody wrote down. Only the pairs an explicit
`#@ conforms_to` created are tagged `from_conforms_to` and only those are emitted.

Together with 1855 this pins both directions: the DECLARED obligation is checked, and
declaring it does not make a conforming class fail.
"""
# pycsl-expected: PASS
_ = 0  # anchor
from typing import Protocol


class P(Protocol):
    #@ ensures \result == 99
    def m(self) -> int: ...


#@ conforms_to P
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 99
    def m(self) -> int:
        return 99
