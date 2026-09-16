r"""Test 1427 - ROUTE #144: the donor base is a `@dataclass` that ALSO writes an explicit `__init__`. `dataclasses._set_new_attribute` never overwrites a class attribute, so the explicit `__init__` wins for THAT class - but `__dataclass_fields__` is still published and the SUBCLASS inherits those names. `\result == 0` PROVED while CPython returns 2. The donor list is `dataclass_fields`, not the donor's own `init_params`.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Ay:
    afld: int

    def __init__(self, afld: int) -> None:
        self.afld = afld


@dataclass
class Cee(Ay):
    cfld: int


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    o = Cee(1, 2)
    return o.cfld
