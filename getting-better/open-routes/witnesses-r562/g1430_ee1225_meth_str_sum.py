from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def h(x: int) -> int:
    return x + 1


@dataclass
class P:
    a: int

    def m(self, y: int) -> int:
        return self.a + y



#@ no_exception \all
def f(k: int, xs: List[int], t: str, p: P) -> int:
    return sum(1 for x in xs if p.m(t))


if __name__ == "__main__":
    try:
        r = f(0, [1, 2], "ab", P(1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
