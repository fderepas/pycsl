r"""Test 1412 — ROUTE #139: `construction_synth` defers a "Constant RHS" to `field_defaults`, whose rule is `isinstance(rhs, ast.Constant)`; Python does not constant-fold, so `self.start = -7` is `UnaryOp(USub, Constant)`. It was neither captured nor marked unknown and fell to the definite witness 0: `\result == 0` PROVED while CPython returns -7.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class C:
    start: int

    def __init__(self) -> None:
        self.start = -7


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.start