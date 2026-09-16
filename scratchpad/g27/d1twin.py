r"""D1 — DEFERRAL AUDIT site 1 (construction_synth.py:83): the deferral says a CONSTANT RHS is
carried by `field_defaults`; `field_defaults` tests `isinstance(rhs, ast.Constant)` and a
negative literal is `UnaryOp(USub, Constant)`."""
_ = 0  # anchor


class C:
    start: int

    def __init__(self) -> None:
        self.start = -7


#@ ensures \result == -7
#@ assigns \nothing
def probe() -> int:
    c = C()
    return c.start
