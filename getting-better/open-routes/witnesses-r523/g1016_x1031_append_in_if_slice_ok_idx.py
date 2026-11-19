from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, s: str) -> int:
    a = ["abc", "defg"]
    if k == 0:
        a.append("z")
    t = 0
    for p in a:
        t += len(p[1])
    return t


if __name__ == "__main__":
    try:
        r = f(0, "z")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
