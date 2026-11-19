from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    d: Dict[str, int]


#@ no_exception \all
def f(r: R, s: str) -> int:
    return r.d.get(s) + 1


if __name__ == "__main__":
    try:
        r = f(R({}), "k")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
