from typing import List, Dict
#@ requires 0 in d
#@ ensures d[0] == \old(d[0])
#@ assigns \nothing
def f(d: Dict[int, List[int]]) -> None:
    d[0].clear()

if __name__ == "__main__":
    x = {0: [1]}; f(x); print(x); assert x[0] == [1]
