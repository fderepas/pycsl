"""Test 0585 — inline a chain that MUTATES an array temp by subscript (arity2.md 2b).

`run` does `work = buf.view(a); buf.store(work, i, v)`. Both calls on the module global `buf`
are inlined. `view` returns its array param, so the inlined `work` becomes an array temp
(`_inl_res = a; work = _inl_res`); `store`'s body `a[i] = v` is then spliced as `work[i] = v`.
Before the 2b fix the array-ness of `work` reached the DECLARATION path (it was not a
`ref 0`) but NOT the per-operation `is_array` site, so the subscript WRITE emitted the
abstract `subscript_set (x:int)` against an `array int` → Why3 type error. The fix routes the
inlined array temp to the concrete `work[i] <- v` (+ `Array.length` bounds check), so the
postcondition `a[i] == v` discharges. RED on the committed baseline; this is the driver the
2b fix flips FAIL→PASS.
"""
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
#@ ensures a[i] == v
#@ assigns a[0..4]
def run(a: list, i: int, v: int) -> None:
    work = buf.view(a)
    buf.store(work, i, v)
