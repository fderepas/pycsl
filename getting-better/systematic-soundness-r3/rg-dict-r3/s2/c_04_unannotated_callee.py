from typing import Set


def mk():
    return [1]


#@ ensures \result == 1
def f() -> int:
    s = {mk()}
    return 1


if __name__ == "__main__":
    print(f())
