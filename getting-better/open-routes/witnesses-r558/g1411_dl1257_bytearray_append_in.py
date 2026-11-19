from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, t: str, b: bytes) -> int:
    xs: List[str] = ["a"]
    xs.append(bytearray(2))
    x = xs[1]
    return 1 if "a" in x else 0


if __name__ == "__main__":
    try:
        r = f(1, "ab", b"ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
