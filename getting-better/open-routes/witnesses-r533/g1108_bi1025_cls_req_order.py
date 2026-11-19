from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses

class Q:
    def __init__(self, k: int) -> None:
        self.k = k


@dataclasses.dataclass(order=True)
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
