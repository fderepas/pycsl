r"""Test 1776 — WITNESS: inlining, in EXPRESSION position, a method that returns no value.

The splice must bind a result variable; a callee whose tail `return` carries no value has
nothing to bind, and continuing would leave the result variable holding whatever was there
before. Refused. One of the refusals `bin/check-refusal-witness-coverage.py` measured as
having no witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Counter:
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns \nothing
    def touch(self) -> None:
        return


g = Counter()


#@ ensures \result >= 0
def read() -> int:
    x = g.touch()
    return 0
