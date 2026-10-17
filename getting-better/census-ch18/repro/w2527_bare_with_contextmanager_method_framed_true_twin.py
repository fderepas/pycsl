from contextlib import contextmanager
from typing import Iterator


class Box:
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    @contextmanager
    def bump(self) -> Iterator[int]:
        self.n = self.n + 1
        yield 0


#@ ensures \result == 1
def f() -> int:
    b = Box()
    with b.bump():
        pass
    return b.n


if __name__ == "__main__":
    print("CPython f() =", f())
