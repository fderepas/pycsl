from typing import Any


#@ requires x == y
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    if isinstance(x, int):
        if not isinstance(y, int):
            return 0
    return 1


if __name__ == "__main__":
    print(f(1, 1.0))
