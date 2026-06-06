"""Test 0586 — negative: a false post about the inlined-mutated array is unprovable (arity2.md 2b).

Same inlined mutate-through-a-temp shape as `0585`, but the postcondition over-claims
`a[i] == v + 1` while the spliced write sets `a[i] = v`. With the 2b fix the inlined array
temp lowers to a CONCRETE `work[i] <- v`, so the VC sees the exact element value and REFUTES
`a[i] == v + 1`. Confirms the fix makes the inlined array path precise, not vacuously typed
or vacuously true.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare


class Buf:
    def __init__(self) -> None:
        pass

    #@ requires \valid(a, 4)
    #@ ensures \result == a
    #@ assigns \nothing
    def view(self, a: list) -> list:
        return a

    #@ requires \valid(a, 4)
    #@ requires 0 <= i and i < 4
    #@ ensures a[i] == v
    #@ assigns a[0..4]
    def store(self, a: list, i: int, v: int) -> None:
        a[i] = v


buf = Buf()


#@ requires \valid(a, 4)
#@ requires 0 <= i and i < 4
#@ ensures a[i] == v + 1
#@ assigns a[0..4]
def run(a: list, i: int, v: int) -> None:
    work = buf.view(a)
    buf.store(work, i, v)
