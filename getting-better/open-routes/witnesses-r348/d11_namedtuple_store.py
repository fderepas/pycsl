from typing import NamedTuple

class N(NamedTuple):
    x: int
    y: int

#@ no_exception \all
#@ ensures \result == 5
def f(n: N) -> int:
    n.x = 5
    return n.x

if __name__ == "__main__":
    print(f(N(1, 2)))
