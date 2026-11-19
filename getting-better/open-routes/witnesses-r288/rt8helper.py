from typing import List

#@ assigns \nothing
def ident(x: List[int]) -> List[int]:
    return x

#@ assigns x
def push(x: List[int]) -> List[int]:
    x.append(7)
    return x

#@ ensures \length(\result) == \length(x)
#@ assigns \nothing
def ident2(x: List[int]) -> List[int]:
    return x
