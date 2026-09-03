"""Test 0982 — a mutating list method on a LOCAL is REFUSED when the lowering erases it.
Tests 0980/0981 found this on a `self.<field>` receiver; the receiver was never the point.

`xs.reverse()` reaches the generic abstract-op fallback and becomes

    val xs_reverse_0 () : int          <-- nullary, no receiver, no `writes`

so the array is untouched and the model even constant-folds the read that follows.
Measured, before this refusal — three shapes, all printing SUCCESS:

    xs: List[int] = [0, 7]; xs.reverse();          return xs[0]   # Python 7
    xs: List[int] = [0, 7]; xs.sort(reverse=True); return xs[0]   # Python 7
    xs: List[int] = [0, 7]; xs.insert(0, 9);       return xs[0]   # Python 9

each under `#@ ensures \result == 0`.

`.append` is NOT in this class: it has a faithful array-local lowering
(`arr[!arr_len] <- v; arr_len := !arr_len + 1`) and is untouched, which is why the whole
819-file reference corpus emits BYTE-IDENTICALLY across this refusal.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def driver() -> int:
    xs: List[int] = [0, 7]
    xs.reverse()
    return xs[0]
