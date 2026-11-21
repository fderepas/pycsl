from dataclasses import dataclass
from typing import Any, Dict, List, Set, Tuple


@dataclass
class D:
    x: int


import dataclasses


#@ no_exception \all
def f(x: D) -> int:
    s = {dataclasses.replace(x)}
    return len(s)


if __name__ == "__main__":
    try:
        print("no violation", f(D(1)))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
