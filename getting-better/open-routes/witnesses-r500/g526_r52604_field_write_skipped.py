from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v: int = 0

    def m(self, n: int) -> int:
        if n > 0:
            return 1
        return 2


g = C()


#@ ensures g.v == 0
def f(n: int) -> int:
    g.v = 0
    g.m(5)
    g.v = 4
    return 0


if __name__ == "__main__":
    try:
        r = f(0)
        if g.v != 0:
            print("VIOLATION contract", g.v)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
