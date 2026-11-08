from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, n: int) -> None:
        self.k = 0
        for x in n:
            self.k = 1


class W:
    def __init__(self, n: int) -> None:
        self.c = C(n)


#@ no_exception \all
def f(n: int) -> int:
    w = W(n)
    return 1


if __name__ == "__main__":
    try:
        r = f(5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
