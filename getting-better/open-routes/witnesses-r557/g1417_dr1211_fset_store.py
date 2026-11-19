from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from typing import NamedTuple, Iterable, Mapping


class NT(NamedTuple):
    a: int
    b: int



#@ no_exception \all
def f(x: FrozenSet[int]) -> int:
    x[0] = 1
    return 1


if __name__ == "__main__":
    try:
        r = f(frozenset({1}))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
