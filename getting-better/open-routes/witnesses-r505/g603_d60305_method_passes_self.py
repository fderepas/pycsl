from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, v: int) -> None:
        self.v = v

    def m(self) -> int:
        return getv(self)

    #@ ensures \result == self.v
    def run(self) -> int:
        return g.m()


#@ ensures \result == c.v
def getv(c: C) -> int:
    return c.v


g = C(1)


#@ ensures \result == 2
def f(n: int) -> int:
    c = C(2)
    return c.run()


if __name__ == "__main__":
    try:
        r = f(0)
        if r != 2:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
