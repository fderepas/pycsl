from typing import Any


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any) -> int:
    if (v := x) is not None:
        return v - v
    return 0


if __name__ == "__main__":
    class S:
        def __sub__(self, o: object) -> int:
            return 7
    print(f(S()))
