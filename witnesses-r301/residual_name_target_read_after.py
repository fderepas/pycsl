from typing import List
#@ requires len(e) == 1
#@ ensures \result == ""
#@ assigns \nothing
def g(e: List[str]) -> str:
    x = ""
    for x in e:
        pass
    return x
