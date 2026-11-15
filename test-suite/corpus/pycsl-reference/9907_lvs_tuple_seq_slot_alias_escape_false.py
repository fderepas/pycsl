r"""Test 9907 -- lvS tuple-seq tail return (expected FAIL): the returned list local ESCAPES into an
alias (`alias = res`) that appends one more element, so value semantics for `res` would be wrong:
`len(\result[0]) == len(xs)` is FALSE in CPython (one extra element) and must NOT prove. Measured:
the pipeline refuses the file upstream (route #81, `[module6-assign]` aliasing a list later appended
to); behind that, the tuple-element seq model refuses an escaping local itself (each occurrence must
be the return slot, a `for` iterable, a test, a `not` operand or a `len` argument). Control: 9905.
"""
# pycsl-expected: FAIL
from typing import List, Tuple


#@ ensures len(\result[0]) == len(xs)
#@ assigns \nothing
def numbered(xs: List[str]) -> Tuple[List[Tuple[str, int]], List[str]]:
    res: List[Tuple[str, int]] = []
    alias = res
    #@ loop invariant len(res) == i
    for i in range(len(xs)):
        x: str = xs[i]
        res.append((x, i))
    alias.append(("z", 0))
    return res, xs


if __name__ == "__main__":
    r = numbered(["a", "b"])
    print("VIOLATION contract" if len(r[0]) != 2 else "result", r)
