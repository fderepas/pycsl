from typing import List

#@ ensures \length(\result) == \length(x)
#@ assigns \nothing
def ident2(x: List[int]) -> List[int]:
    return x
