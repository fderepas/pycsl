from typing import List, Dict, Any, Tuple, Optional

#@ assigns \nothing
def ident(x: List[int]) -> List[int]:
    return x

#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a: List[int] = [0]
    b = ident(a)
    b.append(1)
    return a[0]

if __name__ == "__main__":
    assert f() == 1, f()
