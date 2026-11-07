from typing import List, Dict
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: List[int] = []
    d: Dict[int, List[int]] = {0: a}
    d.get(0, []).append(1)
    return len(a)

if __name__ == "__main__":
    print(f()); assert f() == 0
