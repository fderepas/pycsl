from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, n: int) -> None:
        self.k = sorted([n, "a"])


class D:
    def __init__(self, n: int) -> None:
        self.c = C(n)


class Mk:
    def build(self, n: int) -> int:
        c = C(n)
        return 1


@dataclass
class P:
    c: C


#@ no_exception \all
def f(n: int) -> int:
    p = P(C(n))
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:40])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
