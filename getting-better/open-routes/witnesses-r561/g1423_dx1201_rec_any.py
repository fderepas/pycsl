from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int


class KI:
    def __init__(self, a: int) -> None:
        self.a = a


def h(x: int) -> int:
    return x + 1



#@ no_exception \all
def f(k: int, p: P) -> int:
    return 1 if any(True for x in p) else 0


if __name__ == "__main__":
    try:
        r = f(1, P(1))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
