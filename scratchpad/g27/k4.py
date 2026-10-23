r"""K4 — route #144, second shape: a `ClassVar` member is an ast.AnnAssign and enters
`init_params`, but Python does NOT make it an `__init__` parameter, so the positional binding
is off by one and binds the WRONG field."""
from dataclasses import dataclass
from typing import ClassVar

_ = 0  # anchor


@dataclass
class P:
    k: ClassVar[int] = 10
    x: int
    y: int


#@ ensures \result == 2
#@ assigns \nothing
def probe() -> int:
    p = P(1, 2)
    return p.x
