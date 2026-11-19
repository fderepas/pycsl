from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    s: Optional[str]


def g(k: int) -> int:
    return 1 if isinstance(k, None) else 0



#@ no_exception \all
def f(k: int) -> int:
    return g(k)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
