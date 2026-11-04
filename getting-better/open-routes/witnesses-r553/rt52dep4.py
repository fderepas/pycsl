from typing import Dict, List, Optional


#@ requires len(xs) >= 1
#@ no_exception \all
def gstore(xs: List[int]) -> None:
    xs[0] = None


#@ ensures "a" in d
#@ no_exception \all
def gdstore(d: Dict[str, int]) -> None:
    d["a"] = None


#@ requires len(xs) >= 1
#@ no_exception \all
def gslice(xs: List[int]) -> None:
    xs[0:1] = [None]


#@ no_exception \all
def gret() -> List[int]:
    return [None]
