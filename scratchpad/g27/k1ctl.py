r"""K1-CTL — the same shape WITHOUT inheritance: the binding fires and the false claim must be
REFUSED."""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class D:
    a: int
    b: int


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    d = D(1, 2)
    return d.b
