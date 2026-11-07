r"""Test 1773 — WITNESS: a module GLOBAL bound to a local (`x = g`).

inline.md Phase 3 aliasing ban. A module global is a SINGLE NAMED OBJECT; the inliner
splices method calls on it by name, so binding it to a local would create a second name
for the same object and the splice would stop tracking the writes. Refused rather than
aliased. One of the refusals `bin/check-refusal-witness-coverage.py` measured as having
no witness.
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
def read() -> int:
    x = g
    return x.get()
