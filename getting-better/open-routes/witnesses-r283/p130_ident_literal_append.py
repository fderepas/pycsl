from typing import List

#@ assigns \nothing
def ident(x: List[int]) -> List[int]:
    return x

#@ ensures \result == 9
#@ assigns \nothing
def f() -> int:
    b = ident([5])
    b.append(9)
    return b[0]

if __name__ == "__main__":
    assert f() == 9, f()
