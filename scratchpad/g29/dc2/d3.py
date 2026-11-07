r"""frozen dataclass mutation"""
from dataclasses import dataclass, field
from typing import List
_ = 0  # anchor


@dataclass(frozen=True)
class P:
    a: int


#@ ensures \result == 5
def probe() -> int:
    p = P(1)
    object.__setattr__(p, "a", 5)
    return p.a


if __name__ == "__main__":
    print("CPython:", probe())
