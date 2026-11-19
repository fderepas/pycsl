from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class C:
    s: Set[Any]

    def __post_init__(self) -> None:
        s = self.s
        self.k = sorted(s)


#@ no_exception \all
def f(s: Set[Any]) -> int:
    c = C(s)
    return 1


if __name__ == "__main__":
    try:
        r = f({1, "a"})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
