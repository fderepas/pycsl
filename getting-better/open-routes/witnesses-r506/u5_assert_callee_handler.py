from typing import Any, Dict, List, Optional

#@ ensures \result == 1
def g(n: int, xs: List[int]) -> int:
    assert 10 // n >= 0 or True
    return 1


#@ ensures \result == 1
def f(n: int, xs: List[int]) -> int:
    try:
        return g(n, xs)
    except ZeroDivisionError:
        return 2


if __name__ == "__main__":
    r = f(0, [0])
    print("VIOLATION contract" if r != 1 else "ok", r)
