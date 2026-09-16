r"""G29 f10 — ROUTE #148 family (float literal truncated to int): dataclass keyword-only field default"""
from dataclasses import dataclass, field
from typing import NamedTuple
_ = 0  # anchor


@dataclass
class Cy:
    r: float = field(kw_only=True, default=2.5)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = Cy()
    if c.r > 2:
        return 1
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
