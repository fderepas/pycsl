from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    s: Optional[str]



#@ no_exception \all
def f(o: Optional[int]) -> int:
    return 1 if isinstance(o, None) else 0


if __name__ == "__main__":
    try:
        r = f(None)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
