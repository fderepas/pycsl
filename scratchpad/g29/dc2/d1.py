r"""dataclass default_factory list independence"""
from dataclasses import dataclass, field
from typing import List
_ = 0  # anchor


@dataclass
class P:
    xs: List[int] = field(default_factory=list)


#@ ensures \result == 1
def probe() -> int:
    a = P()
    b = P()
    a.xs.append(1)
    return len(b.xs)


if __name__ == "__main__":
    print("CPython:", probe())
