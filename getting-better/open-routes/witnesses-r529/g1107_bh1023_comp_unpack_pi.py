from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class C:
    xs: List[str]

    def __post_init__(self) -> None:
        xs = self.xs
        self.k = [a for a, b in xs]


#@ no_exception \all
def f(xs: List[str]) -> int:
    c = C(xs)
    return 1


if __name__ == "__main__":
    try:
        r = f(["abc"])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
