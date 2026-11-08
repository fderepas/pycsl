from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: str



#@ no_exception \all
def f(s: str) -> int:
    p = P(+s)
    return len(p.a)


if __name__ == "__main__":
    try:
        r = f("a")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
