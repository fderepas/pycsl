from typing import Set


#@ requires not (1 in y)
#@ ensures \result == False
#@ assigns x
def g(x: Set[int], y: Set[int]) -> bool:
    x.add(1)
    return 1 in y


#@ ensures \result == False
#@ assigns \nothing
def m() -> bool:
    a: Set[int] = set()
    return g(a, a)


if __name__ == "__main__":
    print(m())
