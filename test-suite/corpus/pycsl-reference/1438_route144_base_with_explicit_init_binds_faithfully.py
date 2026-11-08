r"""Test 1438 - ROUTE #144, the FAITHFUL direction for a `@dataclass` base carrying an explicit `__init__`: the subclass's synthesized signature is (afld, cfld) and `Cee(1, 2).cfld` is 2 and PROVES.
"""
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


#@ ensures \result == 2
#@ assigns \nothing
def probe() -> int:
    o = Cee(1, 2)
    return o.cfld
