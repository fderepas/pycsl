r"""Test 1774 — WITNESS: a module GLOBAL passed as a call ARGUMENT (`f(g)`).

The other half of inline.md's Phase 3 aliasing ban: passing the single named object into a
call gives the callee a second name for it, and the inliner's by-name splice would no
longer see the writes. Refused. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Counter:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.n


g = Counter()


#@ ensures \result >= 0
def take(c: Counter) -> int:
    return c.get()


#@ ensures \result >= 0
def read() -> int:
    return take(g)
