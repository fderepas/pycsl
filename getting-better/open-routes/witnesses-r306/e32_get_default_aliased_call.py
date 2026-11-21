from typing import Dict

#@ no_exception \all
#@ requires 1 in d
#@ ensures \result == d[1]
def f(d: Dict[int, int], x: int) -> int:
    return d.get(1, 10 // x)

if __name__ == "__main__":
    assert f({1: 4}, 0) == 4
