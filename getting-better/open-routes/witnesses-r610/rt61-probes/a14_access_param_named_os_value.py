# lvU os.access, param named `os`: the user method's RESULT is lost too (law-free int); the claim
# here is about the effect on a second object passed in.
import os


class C:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def access(self, p: str, m: int) -> int:
        self.n = 5
        return 1


#@ requires os.n == 0
#@ ensures os.n == 0
def f(os: C) -> int:
    if os.access("x", 1):
        return 1
    return 0


if __name__ == "__main__":
    c = C()
    f(c)
    print("VIOLATION contract" if c.n != 0 else "result", c.n)
