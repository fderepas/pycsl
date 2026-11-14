r"""Test 9906 -- lvS tuple-seq tail return (expected FAIL): false twin of 9905. The `seq (string, int)`
slot returned as-is is the REAL accumulator (one element per item), so `len(\result[0]) == 0` is FALSE
for a non-empty input (CPython: 2) and must NOT prove; an erased / empty slot value would prove it.
"""
# pycsl-expected: FAIL
from typing import List, Tuple


#@ ensures len(\result[0]) == 0
#@ assigns \nothing
def numbered(xs: List[str]) -> Tuple[List[Tuple[str, int]], List[str]]:
    res: List[Tuple[str, int]] = []
    #@ loop invariant len(res) == i
    for i in range(len(xs)):
        x: str = xs[i]
        res.append((x, i))
    return res, xs


if __name__ == "__main__":
    r = numbered(["a", "b"])
    print("VIOLATION contract" if len(r[0]) != 0 else "result", r)
