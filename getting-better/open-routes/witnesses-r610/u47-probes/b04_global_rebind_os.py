# u47: `global os` in ANOTHER function rebinds the module name for every function.
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


G = C()


#@ assigns \nothing
def setos() -> None:
    global os
    os = G


#@ ensures \result == 0
def f() -> int:
    setos()
    os.access("x", 1)
    return G.n


if __name__ == "__main__":
    r = f()
    print("VIOLATION contract" if r != 0 else "result", r)
