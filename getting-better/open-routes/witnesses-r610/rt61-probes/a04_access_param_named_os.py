# lvU os.access: a PARAMETER named `os` shadows the module; `os.access(..)` is then a user method
# with an effect (and the model's law-free query writes nothing).
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
def f(os: C) -> int:
    b = os.n
    os.access("x", 1)
    return os.n - b


if __name__ == "__main__":
    r = f(C())
    print("VIOLATION contract" if r != 0 else "result", r)
