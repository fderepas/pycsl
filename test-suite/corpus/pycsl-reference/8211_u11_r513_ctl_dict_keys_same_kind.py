r"""Test 8211 -- route #513 (control, expected PASS; REFUSED at base, whose last-argument reader took the float keys of `Dict[float, int]` as int: PYCSL-R508): comprehensions over the KEYS of a `Dict[float, int]` and the elements of a `Tuple[float, ...]` multiply floats by a float (one kind: no promotion); CPython f({0.5: 1}, (0.5, 1.5)) returns 1
"""
# pycsl-expected: PASS
from typing import Dict, Tuple


#@ no_exception \all
#@ ensures \result == 1
def f(d: Dict[float, int], t: Tuple[float, ...]) -> int:
    v = [k * 0.5 for k in d]
    w = [a * 0.5 for a in t]
    return 1


if __name__ == "__main__":
    print(f({0.5: 1}, (0.5, 1.5)))
