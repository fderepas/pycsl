r"""Test 5703 -- R5-str: the control of 5702. `"zz" in xs` is the REAL element membership
(`arr_mem_str`, defined by its `ensures` as `exists i. xs[i] = x`), so under the guard the
`index` obligation discharges and the result is a valid position holding the needle.
"""
# pycsl-expected: PASS
from typing import List


#@ ensures -1 <= \result < len(xs)
#@ assigns \nothing
def pos(xs: List[str]) -> int:
    if "zz" in xs:
        return xs.index("zz")
    return -1
