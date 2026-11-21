from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

from rt52dep import g


#@ no_exception \all
def f(d: Dict[str, int], k: str, o: Optional[int] = None) -> int:
    v = None
    return g(v)


if __name__ == "__main__":
    try:
        r = f({}, "a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
