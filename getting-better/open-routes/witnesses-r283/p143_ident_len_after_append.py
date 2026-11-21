from typing import List

#@ assigns \nothing
def ident(x: List[int]) -> List[int]:
    return x

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    b = ident([5])
    b.append(9)
    return len(b)

if __name__ == "__main__":
    assert f() == 1, f()
