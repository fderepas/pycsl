from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int
    b: float
    s: str

    def ga(self) -> int:
        return self.a

    def gb(self) -> float:
        return self.b

    def gs(self) -> str:
        return self.s

    #@ no_exception \all
    def m(self) -> int:
        w = self.ga() * self.gb()
        return 1


if __name__ == "__main__":
    try:
        r = P(10**400, 0.5, "ab").m()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
