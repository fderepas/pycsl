from typing import Any, Dict, List, Tuple, Optional


#@ ensures \result == a - b
#@ assigns \nothing
def g(a: int, b: int) -> int:
    return a - b


class S:
    def __sub__(self, o: object) -> int:
        return 7


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    if (v := x) is not None:
        return g(v, v)
    return 0


if __name__ == "__main__":
    print(f(S()))
