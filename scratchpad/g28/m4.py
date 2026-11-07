r"""M4 — the donor base is a @dataclass that ALSO writes an explicit __init__. Python
still publishes __dataclass_fields__, so Cee's synthesized __init__ is (afld, cfld) and
`Cee(1, 2).cfld` is 2."""
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
