from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, s: int) -> None:
        self.k = 0
        for i in range(0, 5, s):
            self.k = i


class W:
    def __init__(self, s: int) -> None:
        self.c = C(s)


#@ no_exception \all
def f(s: int) -> int:
    w = W(s)
    return 1


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
