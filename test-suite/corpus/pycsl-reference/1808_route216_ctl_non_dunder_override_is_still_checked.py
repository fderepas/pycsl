r"""Test 1808 — ROUTE #216, THE TRUE TWIN (expected FAIL): the SAME violation spelled with
an ordinary name IS checked.

One identifier apart from 1805. `Sub.m` returns 0 under `#@ ensures \result == 0` against
`Base.m`'s `\result >= 5`; the emission carries

    let base__m (self: base) : int
    let sub__m  (self: sub)  : int
    goal sub__m_refines_base :

and the goal is unprovable, so the file FAILS — which is correct and is what 1805 reported
SUCCESS for. This file is the completeness half of route #216's decisive signature: it
shows the refusal in 1805 is about the DUNDER and not about the checker being broken.
"""
# pycsl-flags: --check-behavioral-subtyping --memory-model hoare
# pycsl-expected: FAIL
_ = 0  # anchor


class Base:
    #@ ensures \result >= 5
    def m(self) -> int:
        return 5


class Sub(Base):
    #@ ensures \result == 0
    def m(self) -> int:
        return 0
