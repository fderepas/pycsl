from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(d: Dict[str, str], s: str) -> int:
    return 1 if d.get("k") in "abcdefgh" else 0


if __name__ == "__main__":
    try:
        r = f({}, "ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
