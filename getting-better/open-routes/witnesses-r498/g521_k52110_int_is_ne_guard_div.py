from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import copy


class C:
    def __init__(self, v: int) -> None:
        self.v = v


@dataclass
class DC:
    v: int


#@ no_exception \all
def f(n: int) -> int:
    a = n + 1000
    b = n + 1000
    d = 0 if a is b else 1
    return 10 // (1 - d)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
