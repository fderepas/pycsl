from typing import List, Dict
#@ requires 0 in d
#@ ensures len(d[0]) == \old(len(d[0]))
#@ assigns \nothing
def f(d: Dict[int, List[int]]) -> None:
    d[0].append(1)

if __name__ == "__main__":
    x = {0: []}; f(x); print(x); assert len(x[0]) == 0
