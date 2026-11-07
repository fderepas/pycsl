import typing as t
from dataclasses import dataclass

@dataclass
class D:
    x: int
    k: t.ClassVar[int] = 3

#@ no_exception \all
def f() -> int:
    d = D(1, 5)
    return d.x

if __name__ == "__main__":
    print(f())
