from typing import Dict, Optional


class K:
    def __init__(self, n: int):
        self.n = n

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def f(self, x: int, subst: Optional[Dict[str, str]] = None) -> int:
        if subst is None:
            return 1
        return 2

    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def g(self) -> int:
        return self.f(3)

    #@ requires True
    #@ ensures \result == 1
    #@ assigns \nothing
    def h(self) -> int:
        return self.f(3, None)
