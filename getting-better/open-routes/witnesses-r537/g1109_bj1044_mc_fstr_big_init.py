from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

class C:
    def __init__(self, n: int, s: str) -> None:
        match n:
            case s:
                pass
        self.k = f"{s}"


#@ no_exception \all
def f(n: int, s: str) -> int:
    c = C(n, s)
    return 1


if __name__ == "__main__":
    try:
        r = f(10 ** 5000, "a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
