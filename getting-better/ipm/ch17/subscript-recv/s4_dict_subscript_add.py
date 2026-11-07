from typing import Dict, Set

#@ requires True
#@ ensures \result == False
#@ assigns \nothing
def f() -> bool:
    d: Dict[int, Set[int]] = {0: set()}
    d[0].add(1)
    return 1 in d[0]

if __name__ == "__main__":
    print(f())
