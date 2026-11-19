from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, s: str) -> int:
    for c in None:
        break
    return 1


if __name__ == "__main__":
    try:
        r = f(1, "a")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
