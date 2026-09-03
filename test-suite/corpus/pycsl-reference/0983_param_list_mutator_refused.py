"""Test 0983 — the PARAMETER form of test 0982, and the one with the widest reach: a
mutating list method on a caller-supplied list is REFUSED when the lowering erases it.

    #@ requires \length(ys) == 2 and ys[0] == 0
    #@ ensures \result == 0                       <-- FALSE OF THE PROGRAM
    #@ assigns \nothing
    def driver(ys: List[int]) -> int:
        ys.reverse()
        return ys[0]

    [+] Verification SUCCESS! All contracts formally proven.

Real Python returns 7. The emitted body was

    val ys_reverse_0 () : int
    let function driver (ys: array int) : int = let _ = (ys_reverse_0 ()) in (); ys[0]

Note `let function` — the model believed `driver` was PURE, because the only thing that
made it impure had been deleted.

This is the mutation-through-a-parameter family whose dict/set half PyCSL already refuses
loudly ("in-place mutation of dict/set parameter"). The LIST half was silent.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires \length(ys) == 2 and ys[0] == 0
#@ ensures \result == 0
#@ assigns \nothing
def driver(ys: List[int]) -> int:
    ys.reverse()
    return ys[0]
