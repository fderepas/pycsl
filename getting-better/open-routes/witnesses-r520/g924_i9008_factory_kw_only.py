from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import dataclasses


@dataclasses.dataclass(kw_only=True)
class P:
    a: int = dataclasses.field(default_factory=lambda: {"a": 1}["z"])


#@ no_exception \all
def f() -> int:
    p = P()
    return 1


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
