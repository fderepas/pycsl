r"""Test 1416 — ROUTE #139, the faithful direction: `field_defaults` now folds a unary-minus literal with `_const_int_value` (the sibling collector `_collect_class_constants` always did), so `self.start = -7` carries -7 and `\result == -7` PROVES — the true value, not an unconstrained witness.
"""
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