from typing import Any


#@ ensures x == 0 ==> \result == 1
#@ assigns \nothing
def g(x: Any) -> int:
    if x == 0:
        return 1
    return 0


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    return g(v for v in [1])


if __name__ == "__main__":
    print(m())
