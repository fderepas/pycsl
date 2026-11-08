from dataclasses import dataclass
from typing import Dict, List


@dataclass
class D:
    x: int


#@ no_exception \all
def f(m: Dict[str, List[int]]) -> int:
    s = set(m.items())
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f({"a": [1]}))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
