from typing import Dict

#@ no_exception \all
#@ ensures \result == 1
def f(x: int) -> int:
    d: Dict[int, int] = {1: 1}
    return d.get(1, 10 // x)

if __name__ == "__main__":
    assert f(0) == 1
