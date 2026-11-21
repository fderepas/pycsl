from typing import List, Dict, Any, Tuple, Optional

#@ assigns \nothing
def ident(x: List[int]) -> List[int]:
    return x

#@ requires len(a) == 1
#@ ensures \result == 1
#@ assigns \nothing
def f(a: List[int]) -> int:
    b = ident(a)
    b.append(1)
    return len(a)

if __name__ == "__main__":
    assert f([0]) == 1, f([0])
