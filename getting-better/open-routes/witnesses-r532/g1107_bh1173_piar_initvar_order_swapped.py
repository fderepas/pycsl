from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses


@dataclasses.dataclass
class C:
    m: dataclasses.InitVar[str]
    q: dataclasses.InitVar[int]

    def __post_init__(self, q: int, m: str) -> None:
        self.k = q + 1


#@ no_exception \all
def f(n: int) -> int:
    c = C("a", n)
    return 1


if __name__ == "__main__":
    try:
        r = f(5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
