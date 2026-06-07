"""Test 0600 — `p[i]` on a tuple-typed local destructures (0442.md C2).

`p = mk(x)` where `mk` returns a tuple makes `p` a tuple value; `p[0]` must destructure
(`let (_r0, _) = p in _r0`), NOT emit the abstract `subscript_get (x:int)` against the
`(int, int)` tuple (a type error). RED on the prior commit.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result[0] == a
#@ ensures \result[1] == a + 1
#@ assigns \nothing
def mk(a: int) -> tuple:
    return (a, a + 1)


#@ ensures \result == x
#@ assigns \nothing
def run(x: int) -> int:
    p = mk(x)
    return p[0]
