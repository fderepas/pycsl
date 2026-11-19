from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Union, Any, Iterator, Sequence

@dataclass
class D:
    x: int

class R:
    def __init__(self, m: Dict[str, D]) -> None:
        self.m = m

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r.m.get("a")}
    return 1

if __name__ == "__main__":
    print(g(R({"a": D(1)})))
