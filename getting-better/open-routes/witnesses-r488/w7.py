from typing import List, Dict
_ = 0

#@ requires len(a) > 0
#@ ensures \has_key(\result, abs(a[0])) ==> \has_key(\result, abs(a[0]))
#@ assigns \nothing
def f(a: List[int]) -> Dict[int, int]:
    return {x: x + 1 for x in a}
