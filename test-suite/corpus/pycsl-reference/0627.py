"""Test 0627 — seq-model self-concat `a += a` proves length doubling (07-1705 P3).

`a += a` snapshots the same region-free `seq int` value twice (`a := !a ++ !a`), which is sound
(pre-rebind immutable reads) and proves `len(a) == 2 * old len` — the self-aliasing case from the
07-1732 P0 probe, now exercised end-to-end.
"""
# pycsl-flags: --memory-model hoare


#@ ensures \result == 4
#@ assigns \nothing
def double() -> int:
    a = [1, 2]
    a += a
    return len(a)
