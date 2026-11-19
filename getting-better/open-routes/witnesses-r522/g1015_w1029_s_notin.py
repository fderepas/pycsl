from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class S:
    d: Dict[str, str]


#@ no_exception \all
def f(r: S) -> int:
    return 1 if r.d.get("k") not in "ab" else 0


if __name__ == "__main__":
    try:
        r = f(S({}))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
