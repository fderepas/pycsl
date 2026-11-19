from typing import TypeAlias
Num: TypeAlias = float

#@ ensures \result == True
def f(x: Num) -> bool:
    return x % 1 == 0

if __name__ == "__main__":
    assert f(0.5) == True, f(0.5)
