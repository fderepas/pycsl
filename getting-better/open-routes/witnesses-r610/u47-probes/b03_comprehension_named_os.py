# u47: a COMPREHENSION target named `os` (the call is inside the comprehension).
import os
from typing import List


class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 1
    #@ assigns self.n
    def access(self, p: str, m: int) -> int:
        self.n = self.n + 1
        return 1


#@ ensures \result == 0
def f(c: C) -> int:
    xs: List[int] = [os.access("x", 1) for os in [c]]
    return c.n


if __name__ == "__main__":
    r = f(C())
    print("VIOLATION contract" if r != 0 else "result", r)
