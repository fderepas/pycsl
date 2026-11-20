from typing import Callable
#@ ensures \result == 0
#@ assigns \nothing
def g(f: Callable[[int], int], x: int) -> int:
    a = f(x)
    #@ assert a == f(x)
    return 0
if __name__ == "__main__":
    print("ok (assert is a ghost claim; CPython: f(x) at assert point differs)")
