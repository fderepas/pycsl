# pycsl-flags: --memory-model hoare
from typing import List

_ = 0
#@ ensures \result == "b"
#@ assigns \nothing
def f() -> str:
    a: List[List[str]] = [["a"], ["b"]]
    a[0] = a[1]
    a[0][0] = "z"
    return a[1][0]
