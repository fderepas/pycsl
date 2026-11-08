from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple


@dataclass
class D:
    x: int


#@ no_exception \all
def f(d: Dict[str, D]) -> int:
    s = set(d.values())
    return len(s)


if __name__ == "__main__":
    try:
        print("no violation", f({"a": D(1)}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
