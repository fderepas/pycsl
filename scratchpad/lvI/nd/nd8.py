from typing import Dict, Optional


class K:
    def __init__(self, n: int):
        self.n = n

    #@ ensures True
    #@ assigns \nothing
    def f(self, x: int, subst: Optional[Dict[str, str]] = None) -> int:
        try:
            v = subst.get("a", "b")
            return 1
        except AttributeError:
            return 2

    #@ ensures \result == 1
    #@ assigns \nothing
    def g(self) -> int:
        return self.f(3)


if __name__ == "__main__":
    print(K(0).g())
