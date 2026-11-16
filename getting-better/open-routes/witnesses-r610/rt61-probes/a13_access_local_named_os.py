# lvU os.access: a LOCAL named `os` (function scope) shadows the module.
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
def f() -> int:
    os = C()
    os.access("x", 1)
    return os.n


if __name__ == "__main__":
    r = f()
    print("VIOLATION contract" if r != 0 else "result", r)
