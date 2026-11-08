from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses

@dataclasses.dataclass
class Q:
    m: dataclasses.InitVar[int]

    def __post_init__(self, m: int) -> None:
        self.k = m


@dataclasses.dataclass
class P:
    a: int
    b: Any = dataclasses.field(default_factory=Q)


#@ no_exception \all
def f(n: int) -> int:
    p = P(n)
    return p.a


if __name__ == "__main__":
    try:
        r = f(5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
