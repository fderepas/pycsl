# u47: a PARAMETER named `Path` shadows `from pathlib import Path`; `Path.cwd()` is the user
# object's method (an effect the law-free world query drops).
from __future__ import annotations
from pathlib import Path


class P:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def cwd(self) -> str:
        self.n = self.n + 1
        return "/"


#@ ensures Path.n == \old(Path.n)
def where(Path: P) -> int:
    try:
        Path.cwd()
    except OSError:
        return 0
    return 1


if __name__ == "__main__":
    p = P()
    where(p)
    print("VIOLATION contract" if p.n != 0 else "result", p.n)
