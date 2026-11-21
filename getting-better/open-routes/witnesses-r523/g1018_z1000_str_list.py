from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 0
def f(k: int, s: str) -> int:
    a = ["abc", "defg"]
    a.append("z")
    for p in a:
        if p == "z":
            return 1
    return 0


if __name__ == "__main__":
    try:
        r = f(0, "z")
        if not (r == 0):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
