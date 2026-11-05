# Route #561 advice probe: ep1216 (`len([1 in p for x in xs])` of a dataclass `p: P`) with the
# advice followed -- search a container: `p.a in xs`.
from typing import List
from dataclasses import dataclass


@dataclass
class P:
    a: int


#@ no_exception \all
def f(k: int, xs: List[int], p: P) -> int:
    return len([p.a in xs for x in xs])


if __name__ == "__main__":
    print(f(1, [1, 2], P(1)))
