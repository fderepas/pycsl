from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses


@dataclasses.dataclass
class Q:
    v: int = dataclasses.field(default_factory=lambda: [1][3])


@dataclasses.dataclass
class P:
    q: Q


#@ no_exception \all
def f() -> int:
    p = P(Q())
    return 1


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
