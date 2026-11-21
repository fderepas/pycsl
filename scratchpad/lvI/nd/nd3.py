from typing import Dict, Optional


class K:
    def __init__(self, n: int):
        self.n = n

    #@ requires True
    #@ ensures \result >= 0
    #@ assigns \nothing
    #@ no_exception \all
    def f2(self, x: int, subst: Optional[Dict[str, str]] = None) -> int:
        if "a" in subst:
            return 1
        return 0

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def f3(self, x: int, subst: Optional[Dict[str, str]] = None) -> str:
        return subst.get("a", "b")
