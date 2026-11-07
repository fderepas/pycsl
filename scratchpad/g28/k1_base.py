r"""K1-base — the BASE field of a derived @dataclass must bind too."""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class B:
    a: int


@dataclass
class C(B):
    b: int


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    c = C(1, 2)
    return c.a
