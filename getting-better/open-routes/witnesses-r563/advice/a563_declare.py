# advice probe (route #563): witness ef1200 following the advice -- declare the parameter as what you pass
from dataclasses import dataclass
from typing import List


@dataclass
class P:
    a: int

    def m(self, y: str) -> int:
        return self.a + len(y)


#@ no_exception \all
def f(k: int, xs: List[int], t: str, p: P) -> int:
    return p.m(t)
