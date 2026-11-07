from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def nothing() -> None:
    return None



#@ no_exception \all
def f(k: int) -> int:
    xs: List[str] = [1, 2]
    n = 0
    for p in xs:
        n += len(p)
    return n


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
