from typing import Dict


#@ requires not (1 in y)
#@ ensures \result == False
#@ assigns x
def g(x: Dict[int, int], y: Dict[int, int]) -> bool:
    x[1] = 5
    return 1 in y


#@ ensures \result == False
#@ assigns \nothing
def m() -> bool:
    a: Dict[int, int] = {}
    return g(a, a)


if __name__ == "__main__":
    print(m())
