r"""Test 1782 — WITNESS: a bounded TypeVar instantiated with something other than its bound.

`PYCSL-TY3-BOUND`. TY3 checks bounds INVARIANTLY — the concrete type must be EXACTLY the
bound — which is stricter than S1's subtyping and a deliberate divergence-by-strictness
while variance is deferred (GT2). One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Box[T: int]:
    def __init__(self, v: T) -> None:
        self.v: T = v

    #@ ensures True
    def get(self) -> T:
        return self.v


#@ ensures \result >= 0
def use() -> int:
    b: Box[bool] = Box(True)
    return 0
