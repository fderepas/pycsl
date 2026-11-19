from typing import List, Dict
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, List[int]] = {0: [7]}
    d[0].pop()
    return len(d[0])

if __name__ == "__main__":
    print(f()); assert f() == 1
