from typing import Callable
#@ ensures \result == x + 1
#@ assigns \nothing
def g(f: Callable[[int], int], x: int) -> int:
    return x + 1
if __name__ == "__main__":
    print("ok", g(lambda y: y, 1))
