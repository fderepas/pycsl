r"""ensures about a field length"""
from typing import List, Dict
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.xs: List[int] = [1, 2]

    #@ ensures \length(self.xs) == 2
    def check(self) -> None:
        pass


#@ ensures \result == 0
def probe() -> int:
    c = C()
    c.check()
    return len(c.xs) - 2


if __name__ == "__main__":
    print("CPython:", probe())
