r"""dataclass replace-like copy"""
from dataclasses import dataclass, field
from typing import List
_ = 0  # anchor


@dataclass
class P:
    a: int


#@ ensures \result == 1
def probe() -> int:
    p = P(1)
    q = P(p.a)
    q.a = 7
    return p.a + 1


if __name__ == "__main__":
    print("CPython:", probe())
