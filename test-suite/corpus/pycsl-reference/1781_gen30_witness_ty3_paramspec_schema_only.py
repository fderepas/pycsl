r"""Test 1781 — WITNESS: a generic declaring a `ParamSpec` (GT3).

`PYCSL-TY3-GT3`. `ParamSpec` and `TypeVarTuple` are SCHEMA-ONLY: the monomorphizer has no
interpretation for them, so a generic that declares one would be specialized against a
type parameter nothing substitutes. Refused loudly rather than ignored. One of the
refusals `bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Wrap[**P]:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result >= 0
    def get(self) -> int:
        return self.n


#@ ensures \result >= 0
def use() -> int:
    w: Wrap[int] = Wrap()
    return 0
