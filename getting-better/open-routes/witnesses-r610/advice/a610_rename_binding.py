# Route #610 advice followed: "Rename that binding (e.g. `os_obj`) so that `os` names only the
# module." The parameter of 10104 (`os: C`) renamed `os_obj`: `os_obj.access(..)` is now the
# user method, with its contract, and its effect is proved (CPython: 1).
# pycsl-expected: PASS
import os


class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 1
    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    def access(self, p: str, m: int) -> int:
        self.n = self.n + 1
        return 1


#@ ensures \result == 1
def f(os_obj: C) -> int:
    b = os_obj.n
    os_obj.access("x", 1)
    return os_obj.n - b


if __name__ == "__main__":
    r = f(C())
    print("VIOLATION contract" if r != 1 else "result", r)
