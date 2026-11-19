from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self) -> None:
        self.v: int = 0

    def m(self, n: int) -> int:
        return self.k(n)

    def k(self, n: int) -> int:
        if n > 0:
            return 1
        return 2


g = C()


#@ ensures \result == 1
def f(n: int) -> int:
    r = g.m(5)
    return r + 100


if __name__ == "__main__":
    try:
        r = f(0)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
