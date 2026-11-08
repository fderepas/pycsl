from typing import Any, Dict, List, Tuple, Optional


#@ ensures \result == a - b
#@ assigns \nothing
def g(a: int, b: int) -> int:
    return a - b


def h(y):
    return y


class S:
    def __sub__(self, o: object) -> int:
        return 7


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    v = h(x)
    return g(v, v)


if __name__ == "__main__":
    print(f(S()))
