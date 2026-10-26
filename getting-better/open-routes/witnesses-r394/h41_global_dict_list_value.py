from dataclasses import dataclass
from typing import Dict, List


@dataclass
class D:
    x: int


G = {"a": [1]}


#@ no_exception \all
def f() -> int:
    s = {G["a"]}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f())
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
