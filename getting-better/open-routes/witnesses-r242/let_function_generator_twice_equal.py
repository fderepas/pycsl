from typing import Any


#@ assigns \nothing
def r() -> Any:
    return (v for v in [1])


#@ ensures \result == 1
#@ assigns \nothing
def m() -> int:
    if r() == r():
        return 1
    return 0


if __name__ == "__main__":
    print(m())
