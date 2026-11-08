from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import contextlib


@dataclass
class P:
    a: int
    b: float

    def ga(self) -> int:
        return self.a

    def gb(self) -> float:
        return self.b


#@ no_exception \all
def f(p: P) -> int:
    w = p.ga() * p.gb()
    return 1


if __name__ == "__main__":
    try:
        r = f(P(10**400, 0.5))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
