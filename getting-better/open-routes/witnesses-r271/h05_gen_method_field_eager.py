from typing import Iterator
# FALSE: c.bump() only builds a generator; self.n is not incremented. CPython f() == 0.
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    def bump(self) -> Iterator[int]:
        self.n = self.n + 1
        yield 0

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    c = C()
    c.bump()
    return c.n

if __name__ == "__main__":
    print(f())
