from typing import Any


#@ ensures \result == a - b
#@ assigns \nothing
def g(a: int, b: int) -> int:
    return a - b


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    return g(x, x)


if __name__ == "__main__":
    class P:
        def __sub__(self, o: object) -> int:
            return 7

    assert f(P()) == 7
