"""Test 0584 — inline a method RETURNING `array int` in expression position; subscript the
result (arity2.md 2b — operation selection on a read).

`run` evaluates `mk.dup(a)[i]`. The call sits in expression position, so the inliner hoists
it into a fresh result temp (`_inl_res`) bound to the returned array, then the outer `[i]`
reads that temp. Before the 2b fix the temp was an `array int` the read site did NOT
recognise, so it emitted the ABSTRACT `subscript_get (x:int)` against an array → Why3 type
error ("array int but is expected to have type int"). The fix makes the read site recognise
the inlined array temp and emit a concrete `(!temp)[i]`. RED on the committed baseline.
"""
# pycsl-flags: --memory-model hoare


class Maker:
    def __init__(self) -> None:
        pass

    #@ requires \valid(src, 4)
    #@ ensures \result == src
    #@ assigns \nothing
    def dup(self, src: list) -> list:
        return src


mk = Maker()


#@ requires \valid(a, 4)
#@ requires 0 <= i and i < 4
#@ ensures \result == a[i]
#@ assigns \nothing
def run(a: list, i: int) -> int:
    return mk.dup(a)[i]
