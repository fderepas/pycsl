from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, s: int) -> None:
        t = s
        self.k = 0
        for i in range(5, 0, t):
            self.k = i


#@ no_exception \all
def f(s: int) -> int:
    c = C(s)
    return 1


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
