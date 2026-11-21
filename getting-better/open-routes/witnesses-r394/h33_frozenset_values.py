from dataclasses import dataclass
from typing import Dict, List


@dataclass
class D:
    x: int


#@ no_exception \all
def f(m: Dict[str, D]) -> int:
    s = frozenset(m.values())
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f({"a": D(1)}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
