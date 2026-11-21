from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires "k" in d
#@ no_exception \all
def f(d: Dict[str, Optional[int]]) -> int:
    t = 1
    t += d["k"]
    return t


if __name__ == "__main__":
    try:
        r = f({"k": None})
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
