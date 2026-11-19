from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def nothing() -> None:
    return None


def g(x: int) -> int:
    return x + 1


def gs(s: str) -> int:
    return len(s)


class Q:
    def __init__(self) -> None:
        self.a = 1

    def m(self, x: int) -> int:
        return x * 2


@dataclass
class R:
    a: int


#@ no_exception \all
def f(k: int) -> int:
    v = None
    return Q().m(v)


if __name__ == "__main__":
    try:
        r = f(1)
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
