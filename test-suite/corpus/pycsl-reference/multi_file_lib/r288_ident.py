"""Helper for corpus 3370/3371/3373 (route #288): callees that RETURN their list argument."""
from typing import List


#@ ensures \length(\result) == \length(x)
#@ assigns \nothing
def ident2(x: List[int]) -> List[int]:
    return x

