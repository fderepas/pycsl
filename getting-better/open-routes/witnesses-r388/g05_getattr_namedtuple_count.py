from typing import NamedTuple


class P(NamedTuple):
    x: int


#@ ensures \result == 0
def f(p: P) -> int:
    return getattr(p, "count", 0)


if __name__ == "__main__":
    r = f(P(1))
    print("VIOLATION f =", r) if r != 0 else print("no violation")
