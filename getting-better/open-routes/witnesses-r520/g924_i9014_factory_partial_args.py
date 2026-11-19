from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses


@dataclasses.dataclass
class P:
    a: int
    b: int = dataclasses.field(default_factory=lambda: 1 // 0)


#@ no_exception \all
def f() -> int:
    p = P(1)
    return p.a


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
