from dataclasses import dataclass
from typing import Dict, List


@dataclass
class D:
    x: int


import copy


#@ no_exception \all
def f(a: D) -> int:
    b = copy.copy(a)
    s = {b}
    return len(s)


if __name__ == "__main__":
    try:
        print("result", f(D(1)))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
