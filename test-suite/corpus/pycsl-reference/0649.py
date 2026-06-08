"""Test 0649 — seq local meets an int context: the absolute-len boundary (07-2333-rev2 Gap 3).

A seq-promoted (growable) list local is now excluded from the integer `ref 0` pre-declaration, so its
first assignment let-binds a `ref (seq int)` (`_handle_seq_assign`) instead of clashing `seq int` onto
an int ref. `items: list = [0]; items += [1]; return len(items)` proves `== 2` — len is `Seq.length`,
and the seq↔int boundary no longer leaks.
"""
# pycsl-flags: --memory-model hoare


#@ ensures \result == 2
#@ assigns \nothing
def test() -> int:
    items: list = [0]
    items += [1]
    return len(items)
