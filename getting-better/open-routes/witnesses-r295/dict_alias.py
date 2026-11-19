from typing import Dict

#@ assigns \nothing
#@ \trusted
def idd(x: Dict[int, int]) -> Dict[int, int]:
    return x

#@ ensures \result == 1
def f() -> int:
    d: Dict[int, int] = {1: 1}
    e = idd(d)
    e[1] = 2
    return d[1]

if __name__ == "__main__":
    assert f() == 2, f()
