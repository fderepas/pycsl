from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    a: int
    s: str


def two() -> int:
    return 2


class M:
    def __init__(self, n: int) -> None:
        self.n = n

    #@ no_exception \all
    def m(self) -> int:
        c2 = 0
        for c in self.n:
            c2 += 1
        return c2



#@ no_exception \all
def f(k: int) -> int:
    return M(k).m()


if __name__ == "__main__":
    try:
        r = f(3)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
