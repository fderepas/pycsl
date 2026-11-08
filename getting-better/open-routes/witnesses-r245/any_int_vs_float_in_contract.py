from typing import Any


#@ requires x == y
#@ ensures isinstance(x, int) == isinstance(y, int)
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return 0


if __name__ == "__main__":
    print(1 == 1.0, isinstance(1, int) == isinstance(1.0, int))
