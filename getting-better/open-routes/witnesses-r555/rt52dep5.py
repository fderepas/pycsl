from typing import Dict, List, Optional


#@ no_exception \all
def gopt(k: int) -> Optional[int]:
    if k > 0:
        return None
    return k


#@ no_exception \all
def gopts(k: int) -> Optional[str]:
    return None


#@ no_exception \all
def gpipe(k: int) -> int | None:
    return None


#@ no_exception \all
def gget(d: Dict[str, int], k: str) -> Optional[int]:
    return d.get(k)


#@ no_exception \all
def glist(k: int) -> List[Optional[int]]:
    return [None]


class Box:
    #@ no_exception \all
    def __init__(self) -> None:
        self.a = 1

    #@ no_exception \all
    def m(self) -> Optional[int]:
        return None
