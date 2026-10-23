r"""Test 1775 — WITNESS: inlining a global's method with a NON-TAIL `return`.

The inliner splices the callee's body at the call site; a `return` anywhere but the LAST
statement would need control-flow duplication to preserve meaning, so it is refused (a
sound restriction) with the alternative named: verify it by contract. One of the refusals
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
        self.n = 0


g = Counter()


#@ ensures \result >= 0
def read() -> int:
    return g.get()
