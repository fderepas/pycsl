from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from typing import NamedTuple


class P(NamedTuple):
    v: int


class C:
    def __init__(self, p: P) -> None:
        self.k = str((p, 1))


#@ no_exception \all
def f(p: P) -> int:
    c = C(p)
    return 1


if __name__ == "__main__":
    try:
        r = f(P(10 ** 5000))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
