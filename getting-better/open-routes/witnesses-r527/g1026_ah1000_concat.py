from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    s: Optional[str]
    t: str


#@ no_exception \all
def f(r: R) -> int:
    w = r.s + "x"
    return 1


if __name__ == "__main__":
    try:
        r = f(R(None, "ab"))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
