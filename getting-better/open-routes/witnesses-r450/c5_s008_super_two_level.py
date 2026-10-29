from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class B:
    def h(self) -> int:
        return 1

    def __init__(self) -> None:
        self.v = 1


class Q(B):
    def m(self) -> int:
        return 2


class R(Q):
    def g(self) -> int:
        return super().k()


#@ no_exception \all
def f(p: R) -> int:
    return p.g()


if __name__ == "__main__":
    try:
        r = f(R())
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
