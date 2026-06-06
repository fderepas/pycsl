"""Test 0545 — multi-payload projector index `\\payload(x, Ctor, i)` (A5b follow-on).

`\\payload(x, Ctor)` projected the FIRST payload only. The 3-argument form
`\\payload(x, Ctor, i)` selects the i-th payload of a multi-payload constructor:
for `Mk(int, int)`, `\\payload(p, Mk, 1)` is the second component. Under
`\\is_ctor(p, Mk)` the body returns `b` (the 2nd payload), which is exactly
`\\payload(p, Mk, 1)`. Fails today: the 3-arg form is not in the grammar. Flips
when the projector threads an index.
"""
#@ datatype Pair2 = Zero | Mk(int, int)
_ = 0  # anchor


#@ requires \is_ctor(p, Mk)
#@ ensures \result == \payload(p, Mk, 1)
#@ assigns \nothing
def second(p: Pair2) -> int:
    match p:
        case Mk(a, b):
            return b
        case Zero():
            return 0
