r"""dataclass field order and defaults"""
from dataclasses import dataclass, field
from typing import List
_ = 0  # anchor


@dataclass
class P:
    a: int
    b: int = 3


#@ ensures \result == 0
def probe() -> int:
    p = P(1)
    return p.b


if __name__ == "__main__":
    print("CPython:", probe())
