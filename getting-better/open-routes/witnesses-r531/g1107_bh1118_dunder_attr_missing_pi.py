from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class C:
    o: object

    def __post_init__(self) -> None:
        o = self.o
        self.k = o.__len__


#@ no_exception \all
def f(o: object) -> int:
    c = C(o)
    return 1


if __name__ == "__main__":
    try:
        r = f(object())
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
