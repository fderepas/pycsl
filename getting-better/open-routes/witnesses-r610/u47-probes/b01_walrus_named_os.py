# u47: a WALRUS target named `os` shadows the module inside the function.
import os


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
    if (os := c):
        os.access("x", 1)
    return c.n


if __name__ == "__main__":
    r = f(C())
    print("VIOLATION contract" if r != 0 else "result", r)
