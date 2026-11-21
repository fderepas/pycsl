r"""Test 7546 -- route #478 control (expected PASS) under `--memory-model typed`: a list parameter mutated through the modelled element store `a[0] = 5` beside `k *= 2` on an int parameter stays admitted (PROVED at 8aaa864ca and now).
"""
# pycsl-flags: --memory-model typed
from typing import List
#@ requires \length(a) == 2
#@ ensures \result == k * 2
#@ assigns a[0]
def f(a: List[int], k: int) -> int:
    a[0] = 5
    k *= 2
    return k
