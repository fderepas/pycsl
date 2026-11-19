from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int

    def m(self, y: int) -> int:
        return self.a + y


def h(x: int) -> int:
    return x + 1



#@ no_exception \all
def f(k: int, xs: List[int], t: str, d: Dict[str, int], p: P) -> int:
    w = {"a": p.m(t)}
    return 1


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], "ab", {"a": 1}, P(1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
