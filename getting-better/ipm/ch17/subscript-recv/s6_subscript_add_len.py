from typing import Dict, Set

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d: Dict[int, Set[int]] = {0: set()}
    a = len(d[0])
    d[0].add(1)
    b = len(d[0])
    return 1 if a == b else 0

if __name__ == "__main__":
    print(f())
