from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class M:
    def __init__(self) -> None:
        self.n: Optional[int] = None
        self.s: str = "a"

    #@ no_exception \all
    def m(self) -> int:
        w = +self.n
        return 1



#@ no_exception \all
def f(c: M) -> int:
    return c.m()


if __name__ == "__main__":
    try:
        r = f(M())
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
