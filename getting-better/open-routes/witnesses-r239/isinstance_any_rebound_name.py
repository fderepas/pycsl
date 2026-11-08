from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    a = 0
    if isinstance(x, int):
        a = 1
    x = y
    b = 0
    if isinstance(x, int):
        b = 1
    if a == b:
        return 1
    return 0


if __name__ == "__main__":
    print(f(1, "s"))
