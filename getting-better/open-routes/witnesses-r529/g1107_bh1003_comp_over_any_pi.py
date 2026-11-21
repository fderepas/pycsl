from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class C:
    o: Any

    def __post_init__(self) -> None:
        o = self.o
        self.k = [x for x in o]


#@ no_exception \all
def f(o: Any) -> int:
    c = C(o)
    return 1


if __name__ == "__main__":
    try:
        r = f(5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
