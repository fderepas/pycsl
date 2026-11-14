r"""Test 9905 -- lvS tuple-seq tail return CONTROL (expected PASS): in a `-> Tuple[List[Tuple[str,
int]], List[str]]` function, the returned list local `res` grows by the REAL native `(string, int)`
tuple (`Seq.snoc !res (!x, !i)`) and the tail `return res, xs` passes it as the declared `seq (string,
int)` slot as-is (was `materialize_str !res`, a Why3 type error). The loop invariant relates its length
to the index, so `len(\result[0]) == len(xs)` proves. Twin: 9906 (must FAIL).
"""
# pycsl-expected: PASS
from typing import List, Tuple


#@ ensures len(\result[0]) == len(xs)
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
    print("VIOLATION contract" if len(r[0]) != 2 else "result", r)
