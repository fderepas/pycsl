r"""Test 1484 - ROUTE #148 (gen #29, carrier-rerun on gen #27's #139 WATCH row): `self.r = 2.5` in an unannotated field was recorded as `int(2.5)` = 2, so `c.r > 2` was false and `== 0` PROVED; CPython 1. A non-integral float is no longer a `field_defaults` value and route #79 marks the field UNKNOWN.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Cy:
    def __init__(self) -> None:
        self.r = 2.5


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0

