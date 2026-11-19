from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    d: Dict[str, int]

@dataclass
class O:
    r: R


#@ no_exception \all
def f(o: O) -> int:
    return o.r.d.get("k") + 1


if __name__ == "__main__":
    try:
        r = f(O(R({})))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
