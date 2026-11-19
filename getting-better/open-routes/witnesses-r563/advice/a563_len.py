# advice probe (route #563): witness ef1200 following the advice -- pass a value of the declared kind
from dataclasses import dataclass
from typing import List


@dataclass
class P:
    a: int

    def m(self, y: int) -> int:
        return self.a + y


#@ no_exception \all
def f(k: int, xs: List[int], t: str, p: P) -> int:
    return p.m(len(t))
