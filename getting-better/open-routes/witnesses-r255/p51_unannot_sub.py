from typing import Any


def h(z):
    return z


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    v = h(x)
    return v - v


if __name__ == "__main__":
    class S:
        def __sub__(self, o: object) -> int:
            return 7
    print(f(S()))
