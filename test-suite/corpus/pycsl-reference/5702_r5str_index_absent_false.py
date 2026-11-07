r"""Test 5702 -- R5-str (expected FAIL): `xs.index(x)` on a `List[str]` raises ValueError when
`x` is absent, so the model makes presence an OBLIGATION at the call (`arr_index_str` requires
`exists k. xs[k] = x`) -- conservative: the raising path is refused, never assumed away.
(At base `a6ea830ed` this PROVED: the opaque `xs_index_1 <hash>` carried no obligation.) Nothing establishes `"zz" in xs` here
(CPython: `pos(["a"])` raises ValueError), so the call's precondition must NOT prove.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures 0 <= \result < len(xs)
#@ assigns \nothing
def pos(xs: List[str]) -> int:
    return xs.index("zz")
