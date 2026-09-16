r"""M3 — a PLAIN (undecorated) class derived from a @dataclass INHERITS the synthesized
__init__, so `C(7).a` is 7. The model gives the subclass no init_params at all."""
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class B:
    a: int


class C(B):
    pass


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C(7)
    return c.a
